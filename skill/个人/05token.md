---
name: DeepSeek Token Saver
description: 调用 DeepSeek API 时自动压缩输入内容（系统提示、历史对话、用户消息），最多可节省 70% 的 token 消耗。
version: 1.0.0
author: your-name
triggers:
  - pattern: "^节省token[:]?\\s+(.+)$"
    example: "节省token 解释什么是递归"
  - pattern: "^省钱模式[:]?\\s+(.+)$"
    example: "省钱模式 写一个排序算法"
  - pattern: "^compact[:]?\\s+(.+)$"
context:
  - file: "03减少token.md"          # 自动作为系统提示的一部分
    optional: false
env:
  DEEPSEEK_API_KEY: ""              # 请在这里填入你的 DeepSeek API Key，或设置环境变量
steps:
  - type: command
    command: python3 d:\我的文档\桌面\markdown文件\副本\github\note\py\deepseek_saver.py "$match_1" --history .deepseek_history.json --max-response-tokens 500
    timeout: 60
    output: text
  - type: update_context
    file: ".deepseek_history.json"   # 自动保存本轮问答，供下次使用
    merge: append