#!/usr/bin/env python3
"""
DeepSeek Token Saver Skill for Trae
用法:
    echo "你的问题" | python deepseek_saver.py [--history history.json]
    或
    python deepseek_saver.py "你的问题" --history history.json
"""

import sys
import json
import os
import argparse
from pathlib import Path

# 如果没有安装 tiktoken，请先 pip install tiktoken
try:
    import tiktoken
except ImportError:
    print("请先安装 tiktoken: pip install tiktoken", file=sys.stderr)
    sys.exit(1)

# ------------- TokenSaver 类（同前，略作优化）-------------
class TokenSaver:
    def __init__(self, model="deepseek-chat", max_total_tokens=4000, reserve_response=1000):
        self.encoding = tiktoken.encoding_for_model(model)
        self.max_total_tokens = max_total_tokens
        self.reserve_response = reserve_response
        self.max_input_tokens = max_total_tokens - reserve_response

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def trim_text(self, text: str, max_tokens: int, placeholder=" …(已截断)… ") -> str:
        if self.count_tokens(text) <= max_tokens:
            return text
        half = max_tokens // 2
        head = self.encoding.decode(self.encoding.encode(text)[:half])
        tail = self.encoding.decode(self.encoding.encode(text)[-half:])
        return head + placeholder + tail

    def compress_system(self, system: str) -> str:
        import re
        system = system.strip()
        system = re.sub(r'\s+', ' ', system)
        system = re.sub(r'(你是一个|I am an?|You are an?) (AI|人工智能)?(助手|assistant)\.?', '', system, flags=re.IGNORECASE)
        system = re.sub(r'([.!?])\1+', r'\1', system)
        return system.strip()

    def compress_history(self, messages: list, max_history_tokens=1000) -> list:
        if not messages:
            return []
        compressed = []
        used_tokens = 0
        for msg in reversed(messages):
            role = msg.get("role")
            content = msg.get("content", "")
            if not content:
                continue
            if role == "assistant" and len(content) < 10:
                continue
            limited = self.trim_text(content, 300)
            token_cnt = self.count_tokens(limited)
            if used_tokens + token_cnt > max_history_tokens:
                break
            compressed.append({"role": role, "content": limited})
            used_tokens += token_cnt
        compressed.reverse()
        return compressed

    def prepare_request(self, user_message: str, system_prompt: str = "", history=None):
        sys_compressed = self.compress_system(system_prompt) if system_prompt else ""
        sys_tokens = self.count_tokens(sys_compressed)
        user_trimmed = self.trim_text(user_message, 500)
        history_compressed = self.compress_history(history) if history else []
        hist_tokens = sum(self.count_tokens(m["content"]) for m in history_compressed)
        total_input = sys_tokens + self.count_tokens(user_trimmed) + hist_tokens
        if total_input > self.max_input_tokens:
            allowed_user_tokens = max(100, self.max_input_tokens - sys_tokens - hist_tokens)
            user_trimmed = self.trim_text(user_message, allowed_user_tokens)
        new_messages = []
        if sys_compressed:
            new_messages.append({"role": "system", "content": sys_compressed})
        if history_compressed:
            new_messages.extend(history_compressed)
        new_messages.append({"role": "user", "content": user_trimmed})
        return {
            "messages": new_messages,
            "stats": {
                "original_user_tokens": self.count_tokens(user_message),
                "compressed_user_tokens": self.count_tokens(user_trimmed),
                "system_tokens": sys_tokens,
                "history_tokens": hist_tokens,
                "total_input_tokens": total_input
            }
        }

# ------------- 读取 03减少token.md 作为默认系统提示 -------------
def load_system_prompt_from_md():
    md_path = Path(__file__).parent / "03减少token.md"
    if md_path.exists():
        return md_path.read_text(encoding="utf-8")
    return "你是一个节省 token 的助手，请用最简洁的方式回答问题，不要重复用户的话。"

# ------------- 调用 DeepSeek API -------------
def call_deepseek(messages, api_key, model="deepseek-chat", max_tokens=500):
    try:
        from openai import OpenAI
    except ImportError:
        print("请安装 openai 库: pip install openai", file=sys.stderr)
        sys.exit(1)
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.5,
    )
    return response.choices[0].message.content

# ------------- 主入口 -------------
def main():
    parser = argparse.ArgumentParser(description="DeepSeek Token Saver Skill")
    parser.add_argument("user_input", nargs="*", help="用户问题（如果不提供，则从 stdin 读取）")
    parser.add_argument("--history", type=str, help="历史对话 JSON 文件路径（可选）")
    parser.add_argument("--system", type=str, help="额外的系统提示（会与 03减少token.md 合并）")
    parser.add_argument("--api-key", type=str, default=os.getenv("DEEPSEEK_API_KEY"), help="API Key，也可设置环境变量 DEEPSEEK_API_KEY")
    parser.add_argument("--max-response-tokens", type=int, default=500, help="响应最大 token 数")
    args = parser.parse_args()

    if not args.api_key:
        print("错误: 请提供 --api-key 或设置环境变量 DEEPSEEK_API_KEY", file=sys.stderr)
        sys.exit(1)

    # 获取用户输入
    if args.user_input:
        user_input = " ".join(args.user_input)
    else:
        user_input = sys.stdin.read().strip()
    if not user_input:
        print("错误: 没有提供用户问题", file=sys.stderr)
        sys.exit(1)

    # 加载系统提示（默认来自 03减少token.md）
    base_system = load_system_prompt_from_md()
    if args.system:
        base_system = base_system + "\n\n" + args.system

    # 加载历史对话（如果提供）
    history = []
    if args.history and Path(args.history).exists():
        with open(args.history, "r", encoding="utf-8") as f:
            history = json.load(f)

    # 压缩请求
    saver = TokenSaver(model="deepseek-chat", max_total_tokens=4096, reserve_response=args.max_response_tokens + 200)
    prepared = saver.prepare_request(user_input, base_system, history)

    # 可选：输出压缩统计到 stderr（不影响返回结果）
    sys.stderr.write(json.dumps(prepared["stats"], indent=2) + "\n")

    # 调用 API
    answer = call_deepseek(
        prepared["messages"],
        api_key=args.api_key,
        max_tokens=args.max_response_tokens
    )
    print(answer)  # Trae 会捕获这个输出作为 skill 的回复

if __name__ == "__main__":
    main()