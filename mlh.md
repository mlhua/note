<style>
body {
    font-family: '楷体', 'KaiTi', '华文楷书', STKaiti;
    font-size: 16px;
}
</style>

# 开发过程笔记
---
# Markdown使用

## 一、符号作用
1. **#** 表示一级标题，**##** 表示二级标题，以此类推。
2. **\*** 表示列表项，**-** 也可以表示列表项。
3. **\>\s** 表示引用，引用内容会被缩进。
4. **\*\*** 表示加粗，\* 表示斜体。
5. **\`\`\`** 表示代码块，\` 表示行内代码。
6. **- []\s** 表示复选框，[] 表示未选中，[x] 表示选中。
7. **\-\s** 表示任务列表项，\[\s\] 表示未完成，\[\*\] 表示已完成。
8. 表示序号         
   1. 第一项
   2. 第二项
   3. 第三项
## 二、修改样式
 像头文件一样修改样式，用style标签包裹样式代码，样式代码中可以使用css语法。

## 三、如何添加颜色

如下所示  
<span style="color: #f12d2d;">鲜红</span>    <!-- 红 -->
<span style="color: #00FF00;">鲜绿</span>    <!-- 绿 -->
<span style="color: #0000FF;">鲜蓝</span>    <!-- 蓝 -->
<span style="color: #FFD700;">金色</span>    <!-- 金 -->
<span style="color: #8B4513;">棕色</span>    <!-- 棕 -->
<span style="color: #1E90FF;">道奇蓝</span>  <!-- 亮蓝 -->
<span style="color: #000000;">黑色</span>    <!-- 黑 -->

## 四、颜色定义

<span style="color: #f566d1;">牢骚话</span>  
<span style="color: #f12d2d;">重点</span>  
<span style="color: #FFD700;">注意</span>  
<span style="color: #5bfaff;">时间</span>

# Docker 使用笔记

## 一、Docker 是什么？
Docker 是一个开源的容器化平台，可以将应用程序及其依赖打包到轻量级、可移植的容器中。容器在不同环境中运行结果一致，解决了"在我电脑上能运行"的问题。

## 二、Docker 安装（Ubuntu 20.04）
```bash
# 使用清华镜像源加速
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 将当前用户加入 docker 组（避免每次用 sudo）
sudo usermod -aG docker $USER
newgrp docker  # 刷新用户组

# 验证安装
docker --version
docker run hello-world
```

## 三、Docker 基本命令
```bash
# 查看所有容器（包括已停止的）
docker ps -a

# 查看正在运行的容器
docker ps

# 查看本地镜像
docker images

# 删除容器
docker rm 容器ID

# 删除镜像
docker rmi 镜像ID
```

## 四、ARM64 Qt6 构建环境使用

### 1. 运行容器（挂载共享目录）
```bash
# 参数说明：
# --privileged: 特权模式，容器可以访问主机设备
# -v 主机目录:容器目录: 挂载共享文件夹
# -it: 交互式终端
# bash: 启动后进入 bash

docker run --privileged \
  -v /mnt/hgfs/WinShare/qt:/root \
  -it terra-arm64-qt6-build-addmd:v2 \
  bash
```

### 2. 在容器内编译项目
```bash
# 进入容器后（已经在 /root 目录）
cd /root

# 创建构建目录（保持源码干净）
mkdir -p build && cd build

# 配置 CMake（关键！指定 Qt6 路径）
cmake .. -DCMAKE_PREFIX_PATH=/usr/lib/aarch64-linux-gnu/cmake/Qt6

# 编译（用所有 CPU 核心加速）
make -j$(nproc)

# 编译完成后，生成的可执行文件
ls -la appPunpQT
file appPunpQT  # 确认是 ARM64 架构
```

### 3. 环境变量（可选）
如果 Qt6 命令不在 PATH 中：
```bash
export PATH=/usr/bin/qt6/bin:$PATH
```

## 五、常见问题解决

### 权限问题
```bash
# 错误：permission denied while trying to connect to Docker daemon socket
# 解决：将用户添加到 docker 组
sudo usermod -aG docker $USER
newgrp docker
```

### CMake 找不到 Qt6
```bash
# 错误：Could not find a package configuration file provided by "Qt6"
# 解决：正确设置 CMAKE_PREFIX_PATH
find /usr -name "Qt6Config.cmake" 2>/dev/null  # 先查找实际位置
cmake .. -DCMAKE_PREFIX_PATH=找到的路径
```

### 编译输出文件在哪？
编译生成的可执行文件在 `build/` 目录下：
```bash
/root/build/appPunpQT  # 在容器内
# 由于挂载了共享目录，主机上也能看到：
/mnt/hgfs/WinShare/qt/build/appPunpQT
```

## 六、镜像迁移
将镜像复制到另一台机器：
```bash
# 保存镜像
docker save terra-arm64-qt6-build-addmd:v2 | gzip > qt6-image.tar.gz

# 传输文件（用 U 盘或 scp）
cp qt6-image.tar.gz /mnt/hgfs/WinShare/

# 在目标机加载
docker load -i qt6-image.tar.gz
```
 
## 七、Linux中串口虚拟
### 原理
主要用SOCAT工具，核心指令如下socat -d -d PTY,link=/tmp/ttyV0,raw,echo=0 PTY,link=/tmp/ttyV1,raw,echo=0，这样他们就会形成一对虚拟串口，数据在它们之间传输。用于模拟串口通信,但是建立的默认是只能root用户访问的，所以需要修改权限，用如下指令：socat -d -d PTY,link=/tmp/ttyV0,raw,echo=0,perm=0666 PTY,link=/tmp/ttyV1,raw,echo=0,perm=0666，这样就可以让所有用户都能访问这个串口了。

### 测试连通方法
在一个终端中输入cat /tmp/ttyV0（等待接收）  
在另一个终端中输入echo "Hello World" > /tmp/ttyV1（发送数据）  
即可在第一个终端看到Hello World，说明通信成功。

### 疑问解答
1. 为什么使用socat  
    因为它可以创建虚拟串口对，并且支持多种协议，非常适合模拟串口通信。
2. 他创造出来的虚拟串口在哪个位置  
   在/tmp/ttyV0和/tmp/ttyV1。
3. 为什么在这个目录下？  
    因为/tmp目录是系统临时目录，用于存储临时文件和目录。而/tmp目录下的文件和目录在系统重启后会被自动删除，所以可以安全地用于临时存储。
4. 为什么调用核心指令后，显示socat[4397] N PTY is /dev/pts/3
    在 Linux 底层，系统不会真的直接生成一个叫 ttyV0 的设备，而是从内核的伪终端池（/dev/pts/ 目录）中分配一个编号，这里分配的是编号为3的伪终端。所以，/dev/pts/3 就是 ttyV0 对应的设备。 
 ---

# Socat 笔记

## 一、介绍
Socat 是一个用于创建虚拟串口对的工具，它可以在 Linux 系统中模拟串口通信。

## 二、使用

### 1.基础命令：创建一对互联的虚拟串口
```bash
socat -d -d PTY,link=/tmp/vpts0,raw,echo=0 PTY,link=/tmp/vpts1,raw,echo=0
```
参数详解：  
-d -d: 输出调试信息（Fatal, Error, Warning, Info）。建议加上，这样你可以看到 socat 成功创建了哪些设备文件。  
PTY: 指定地址类型为伪终端。  
link=/tmp/vpts0: 为该伪终端创建一个符号链接（快捷方式）。你可以自定义路径，如 /dev/ttyV0（注意权限）。  
raw: 原始模式。不处理特殊字符（如 Ctrl+C），确保数据透明传输。  
echo=0: 禁用回显。防止发送的数据被原样弹回。  

### 2.查看串口的数据
在一个终端中输入cat /tmp/vpts0（等待接收）    
但是一般我们发送的都是十六进制的数据，因此需要使用xxd命令来查看，如下：
```bash
xxd -p /tmp/vpts0
```
但是我们最常用的是使用socat自带的指令来完成这个操作，使用指令如下
```bash
#1. -v (Verbose) —— 显示传输方向和元数据
#2. -x (Hexadecimal) —— 显示十六进制数据
socat -v -x PTY,link=$HOME/vpts0,raw,echo=0 PTY,link=$HOME/vpts1,raw,echo=0,b115200
```
### 3.发送数据
```bash
#在一个终端中输入
echo -e -n "\x01\x03\x00\x00\x00\x0a\xc5\xcd" > ~/vpts0 #主机的请求读数据
echo -e -n "\x01\x03\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa3\x67" > ~/vpts0 #从机的答复
```

## 三、常见问题
### 波特率设置
虽然虚拟串口不需要波特率，但是以往万一有些情况需要检查波特率是否一致，所以还是可以设置一下的。
```bash
socat -d -d PTY,link=/tmp/vpts0,raw,echo=0 PTY,link=/tmp/vpts1,raw,echo=0,b115200
```
### <span style="color: #f12d2d;">路径问题</span> 
我在用这个的时候，是因为开发QT项目所需，起初是放在/tmp目录下的，但是在程序中，发现一直找不到这个文件，后面甚至怀疑是不是库不支持访问虚拟串口，经过好多次的排查，终于找到问题所在，原来定义虚拟串口需要在$HOME目录下，而不是/tmp目录下，因为我登录的当前账号是没办法直接访问/tmp目录下的内容，尽管我是用的sudo命令打开的软件，这个坑真的坑了我好久好久。
因此，我建议在$HOME目录下定义虚拟串口，而不是/tmp目录下，命令如下
```bash
socat -d -d PTY,link=$HOME/vpts0,raw,echo=0 PTY,link=$HOME/vpts1,raw,echo=0,b115200
```

### 权限问题
权限问题就在于，创建虚拟串口后，用ls -l命令查看权限，发现是0666，说明所有用户都可以访问这个串口了，如果不是的话就改一下用户权限，用如下指令：
```bash
chmod 0666 /tmp/vpts0 /tmp/vpts1
```

# CAN通讯

## 一、CAN 是什么：多主异步串行总线
CAN (Controller Area Network) 最初由 Bosch 开发，其核心定义是：一种基于优先级仲裁的、多主从的、半双工异步串行通讯协议。  
多主性： 每个节点都是平等的，不存在 I2C 那种 Master 对 Slave 的轮询。  
非破坏性仲裁： 依靠 ID 的位电平竞争，高优先级消息不会因为冲突而损坏。  
高容错： 内置 5 种错误检测机制，是工业级可靠性的代名词。  

## 二、物理接口与电平特性
1.差分信号接口CAN 必须使用 CAN_H 和 CAN_L 两根线。  
显性电平（Dominant, 逻辑 0）： $V_{diff} = V_H - V_L \approx 2.0V$。此时驱动器强行拉开电位。  
隐性电平（Recessive, 逻辑 1）： $V_{diff} \approx 0V$。此时驱动器高阻态，靠 120Ω 终端电阻回弹。

2.常见物理接口
DB9 接口： 标准工业接口（Pin 2 为 L，Pin 7 为 H）。  
端子排： 常见的工业模块接口（H, L, GND）。  
收发器芯片： 如 TJA1042, SN65HVD230。它负责将 MCU 的 TTL 电平（TX/RX）转换为总线的差分电平。  

## 三、协议帧结构（Standard CAN 2.0A 为例）
一个完整的 CAN 数据帧包含 7 个部分：  
1.SOF (Start of Frame)： 1 bit 显性电平。  
2.Arbitration Field (仲裁域)： 11 bit ID + RTR 位（远程帧标志）。ID 越小电平 0 越多，优先级越高。  
3.Control Field (控制域)： 包含 IDE（扩展标志）、保留位和 DLC（数据长度码，0-8 字节）。  
4.Data Field (数据域)： 0 到 8 字节的实际负载。  
5.CRC Field (校验域)： 15 bit CRC 序列 + 1 bit 界定符。  
6.ACK Field (应答域)： 发送方发 1（隐性），接收方如果收到必须回填 0（显性）。  
7.EOF (End of Frame)： 7 bit 连续隐性电平，表示结束。  

## 四、CAN的配置
CAN主要配置的内容如下：波特率与位定时 (Bit Timing)；过滤器配置 (Filter/Acceptance Mask)；报文发送与接收对象 (Message Objects/Mailboxes)；工作模式 (Operating Modes)；中断与错误处理 (Interrupts & Errors)；应用层参数 (DBC 关联配置)
```
1. 波特率与位定时 (Bit Timing)
这是最基础的配置。如果节点之间的“节拍”不一致，通讯会直接报错。
时钟分频 (Prescaler)： 确定 CAN 控制器的基本工作时钟。
时间段配置 (Phase Segments)： 将一个位时间（Bit Time）划分为 Sync_Seg、Prop_Seg、Phase_Seg1 和 Phase_Seg2。
采样点 (Sample Point)： 决定在一位的什么位置读取数据。通常车载 CAN 设置在 80% 左右，工业领域可能略有不同。
SJW (Synchronization Jump Width)： 允许的时钟补偿宽度，用于处理节点间的频率偏差。

2. 过滤器配置 (Filter/Acceptance Mask)
CAN 总线是广播式的，你的节点会收到总线上所有的消息。为了不让 CPU 被无关信息淹没，需要设置硬件过滤器。
过滤器模式： * 标识符列表模式： 只接收特定 ID 的报文。
掩码模式 (Mask Mode)： 通过掩码屏蔽掉 ID 中的某些位，从而接收一组符合规律的 ID。
ID 类型： 指定接收标准帧（11位）还是扩展帧（29位）。

3. 报文发送与接收对象 (Message Objects/Mailboxes)
软件需要为频繁使用的报文开辟“窗口”。
发送邮箱 (Tx Mailbox)： 配置优先级（按 ID 大小或先后顺序）和发送缓冲区。
接收 FIFO/邮箱 (Rx FIFO)： 配置缓存深度，防止报文来不及处理而被覆盖。

4. 工作模式 (Operating Modes)
根据调试或运行需求，通常有以下几种模式可选：
Normal Mode： 正常收发模式。
Loopback Mode (回环模式)： 用于自测，发出的报文自己能收到，不影响总线。
Silent Mode (静默模式)： 只听不发，常用于总线监听或波特率自动识别。
Sleep Mode： 低功耗模式。

5. 中断与错误处理 (Interrupts & Errors)
为了提高实时性，软件通常需要配置中断回调函数：
接收中断： 收到新数据时触发。
发送完成中断： 数据成功发出后触发。
错误中断： 当总线发生位错误、填充错误或进入 Bus-Off 状态时报警。
注意： 在软件层面，通常还需要编写 Bus-Off 恢复逻辑，确保节点在因干扰脱离总线后能自动尝试重连。

6. 应用层参数 (DBC 关联配置)
如果你在做更高级的开发，通常需要结合 DBC 文件（数据库文件）进行配置：
周期性 (Cycle Time)： 报文是每 10ms 发一次，还是触发式发送。
信号解析： 起始位、长度、大小端（Intel/Motorola）、偏移量（Offset）和缩放系数（Factor）。
```
## 五、CAN的QT程序实现
1. 用socket创建一个CAN套接字 程序是int s = socket(PF_CAN, SOCK_RAW, CAN_RAW);  
这里 PF_CAN 表示 CAN 协议族，SOCK_RAW 表示原始套接字，CAN_RAW 表示使用原始 CAN 报文。  
套接字 (Socket)：操作系统提供的一种通信接口，用来屏蔽底层协议细节。常见的有 TCP/UDP 套接字。  
SocketCAN：Linux 内核提供的一套机制，把 CAN 总线接口抽象为套接字。开发者可以通过 AF_CAN 域来创建 CAN 套接字。
2. 使用ioctl获取CAN设备的接口索引  
ioctl(s, SIOCGIFINDEX, &ifr);   
为什么不直接用名字？： bind 函数需要的参数是一个整数索引（ifindex），而用户只知道字符串名字（"vcan0"）。ioctl 配合 SIOCGIFINDEX 命令充当了查字典的角色。  
3. 把接口索引绑定到套接字上  
bind(s, (struct sockaddr *)&addr, sizeof(addr))   
逻辑含义：执行 bind 之前，这个 Socket 只是一个空壳；执行 bind 之后，这个 Socket 就正式与物理（或虚拟）的 CAN 硬件挂钩了。
4. 数据交互 (Read/Write)
使用标准的 Linux 文件操作：  
发送：write(s, &frame, sizeof(struct can_frame));  
接收：read(s, &frame, sizeof(struct can_frame));  
5. 资源释放
关闭：close(s);

## 六、CAN的QT程序测试
1. 安装can-utils用于linux测试  
```bash
sudo apt update
sudo apt install can-utils
```
2. 启动虚拟CAN设备
```bash
# 1. 加载内核模块
sudo modprobe vcan
# 2. 创建虚拟 CAN 设备
# 如果设备已存在，先删除（确保干净环境，可选）
sudo ip link delete vcan0>/dev/null
# 3. 添加并启动设备
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```
3. 查看虚拟CAN设备
```bash
ip link show
```
4. 查看数据传输情况
```bash
candump vcan0
```
5. 模拟发送数据
```bash
# 向 can0 发送 ID 为 123，数据为 11 22 33 44 55 66 77 88 的帧
cansend vcan0 123#1122334455667788
```
6. 把两个虚拟CAN设备连接起来
用这个的时候需要系统加载can-gw的模块，因为cangw 就像是一个“路由器”，负责把 vcan0 的数据转发到 vcan1。但这个“路由功能”在 Linux 内核里是一个独立的模块，默认情况下很多系统（尤其是虚拟机或嵌入式板卡）没有加载它。
```bash
# 加载can-gw模块
sudo modprobe can-gw
# 将 vcan0 的流量转发到 vcan1
sudo cangw -A -s vcan0 -d vcan1 -e
# 将 vcan1 的流量转发到 vcan0
sudo cangw -A -s vcan1 -d vcan0 -e
```
## 七、CAN在实体机上的启动
为了方便我写成了一条指令
```bash
#就是开启can0和can1，并且设置波特率为500000
ip link set can0 down && ip link set can0 type can bitrate 500000 && ip link set can0 up && ip link set can1 down && ip link set can1 type can bitrate 500000 && ip link set can1 up
```



# QT的使用
## 一、启动两个QT程序
启动两个QT程序不用同时打开两个工程的，可以用指令来打开编译好的可执行文件，同时可以使用传入参数的方法来区分两个程序，编译好的文件和需要传入的参数例子如下（开两个终端）
```bash
root@lubancat-vm:/home/lubancat/work/qt/punp/qt/build/Desktop_Qt_6_8_3-Debug# sudo ./appPunpQT helper
root@lubancat-vm:/home/lubancat/work/qt/punp/qt/build/Desktop_Qt_6_8_3-Debug# sudo ./appPunpQT master
```
## QT编译后生成的文件


## QT的编译过程--把什么变成什么

# iperf3
## 一、iperf3是什么
iperf3是一个网络性能测试工具，主要用于测量网络带宽和延迟。它可以在客户端和服务器之间进行数据传输，并提供详细的性能指标，如带宽、抖动和丢包率等。iperf3支持TCP和UDP协议，可以用于评估网络连接的质量和性能，常用于网络调试、性能优化和容量规划等场景。
## 二、iperf3的使用
iperf3的使用方法如下：
```bash
#启动服务器端（负责接收数据）
iperf3 -s
#服务端指令
-s, --server: 启动服务端模式。
-D, --daemon: 后台运行。作为开发，我们经常把它挂在后台服务器上。
-1, --one-off: 接收并处理完一次测试请求后就自动退出。
#启动客户端（负责发送数据）
iperf3 -c 服务器IP地址
#客户端指令
-c [host]: 启动客户端并连接到指定的服务端 IP。
-t, --time [seconds]: 测试时长，默认 10 秒。
-R, --reverse: 反向模式（服务端发，客户端收）。这在排查非对称带宽（如下行带宽）时非常有用。
#其他常用选项
-u, --udp: 使用 UDP 协议。默认是 TCP。
-b, --bandwidth [N[KM]]: 限制带宽。对于 UDP 测试，必须指定这个参数，否则它会默认以 1Mbps 运行。
-P, --parallel [n]: 多线程测试。启动多个并发流。如果单线程跑不满带宽（通常受限于单核 CPU 性能或 TCP 窗口），记得加这个。
-w, --window [size]: 设置套接字缓冲区大小（即 TCP 窗口大小）。在长距离、高延迟的网络中，这个值调大能显著提升吞吐量。
-M, --set-mss [n]: 设置 TCP 最大分段大小（MSS），用于测试 MTU 限制。
-4 / -6: 强制使用 IPv4 或 IPv6。
-Z, --zerocopy: 使用零拷贝发送数据。这能显著降低测试时的 CPU 负载。
-O, --omit [n]: 忽略前 n 秒的测试数据。这是为了规避 TCP 慢启动（Slow Start）对最终平均值的影响。
-B, --bind [host]: 绑定到指定的本地 IP 地址。这在多网卡环境中很有用，可以指定测试走哪个接口。
```
## 三、iperf3的输出内容



# UDP
## 一、UDP是什么

## 二、UDP怎么用




# TCP/IP模型
## 1.TCP/IP模型是什么
是互联网最基本的通信协议集合，定义了数据如何在网络中从一台设备传输到另一台设备。它采用分层结构，每一层负责不同的通信功能。和他同等级的还有OSI模型。
### 1.1. TCP/IP模型的组成
四层结构（从下到上）：  
1. 网络接口层（链路层）    
负责通过物理网络（如以太网、Wi-Fi）发送和接收数据帧。  
处理硬件地址（MAC地址）、数据封装成帧。  
2. 网络层（互联网层）  
核心协议：IP协议（IPv4/IPv6）。  
负责数据包（packet）的寻址和路由，实现跨网络传输。  
提供逻辑地址（IP地址），决定数据从源到目标的路径。  
3. 传输层（传输层）  
核心协议：TCP 和 UDP。  
TCP（传输控制协议）：面向连接、可靠传输（确认、重传、流量控制）。适用于网页浏览、文件下载、电子邮件。  
UDP（用户数据报协议）：无连接、不可靠但高效。适用于实时应用（语音、视频、DNS查询）。  
4. 应用层（应用层）  
直接为应用程序提供网络服务。常见协议：HTTP（网页）、FTP（文件传输）、SMTP（邮件）、SSH（远程登录）、DNS（域名解析）。  
数据单位称为报文（message）。  




 # linux学习
 ## Linux指令
 ### 常用
 ssh 用户名@IP地址
 
### 1、LS
```bash
ls -l #长格式显示：权限、所有者、大小、修改时间等
ls -a #显示所有文件，包括隐藏文件
-t #按修改时间排序，最近的文件排在前面
-r #反转排序顺序，配合 -t 使用可以让最旧的文件排在前面
#我有时候经常这样用 -ltr
```
使用 -l 后显示出来的一串内容如下
```bash
drwx------ 2 lubancat lubancat 4096 3月  23 08:34 tracker-extract-files.1000
drwxrwxrwt 2 root     root     4096 3月  23 08:33 VMwareDnD
drwx------ 2 root     root     4096 3月  23 08:33 vmware-root_905-4013330159
lrwxrwxrwx 1 lubancat lubancat   10 3月  23 09:48 vpts0 -> /dev/pts/2
lrwxrwxrwx 1 lubancat lubancat   10 3月  23 09:48 vpts1 -> /dev/pts/3
```
字段解释  
lrwxrwxrwx
第一个字母 l 表示这是一个 符号链接 (link)。
后面 9 个字符是权限位：
r = 可读 (read)
w = 可写 (write)
x = 可执行 (execute)
三组分别对应 所有者 (user)、所属组 (group)、其他人 (others)。
所以这里是 rwxrwxrwx，表示所有人都可以读、写、执行这个链接。

1
表示硬链接数。对于普通文件是硬链接数量，对于目录是子目录数量。符号链接通常是 1。
lubancat（所有者）
文件的拥有者用户名。
lubancat（所属组）
文件所属的用户组。

10
文件大小（字节数）。这里是符号链接本身的长度，即链接路径字符串的长度（/dev/pts/2 有 10 个字符）。

3月 23 09:48
文件的最后修改时间。

vpts0
文件名。

-> /dev/pts/2
符号链接指向的目标路径。这里表示 vpts0 实际上指向 /dev/pts/2。

### 2、rm
```bash
#删除文件夹强制（非空）
rm -rf 文件名
-r	--recursive	递归删除。删除目录及其下的所有内容。
-f	--force	强制删除。忽略不存在的文件，不提示确认。
-i	--interactive	交互模式。删除前逐一询问你是否确认（更安全）。
-v	--verbose	显示过程。列出每一个正在被删除的文件名。
```

### 3、grep
从文件中通过关键字过滤文本行    
语法：grep [-n] 关键字 文件路径  
-n	--number	显示行号。  

### 4、wc
统计文件中的行数、字数和字符数等  
语法：wc [-lwm] 文件路径  
-l	--lines	统计行数。  
-w	--words	统计单词数。  
-m	--chars	统计字符数。  

### 5、管道符“|”
|	--pipe	管道符。将前一个命令的输出作为后一个命令的输入。  
练习：cat test.txt | grep "itcast" | wc -l # 统计包含 itcast 关键字的行数  

### 6、echo命令
echo "文本内容" # 输出文本内容到终端  

### 7、反引号'
反引号（`）用于执行命令并返回其输出。  

### 8、重定向符号
```bash
>	--redirect	重定向。将命令的输出重定向到文件。  
<	--redirect	重定向。将文件的输入重定向到命令。  
&	--append	追加。将命令的输出追加到文件。  
&	--append	追加。将文件的输入追加到命令。  
>	--redirect	重定向符号。将命令的输出重定向到文件。  
>>	--append-redirect	重定向符号。将命令的输出追加到文件。  
```

### 9、tail
使用tail命令查看文件的最后几行内容
```bash
tail -n 文件路径 # 查看文件的最后 n 行内容
```
### 10、top
直接输入top命令，可查看cpu的运行情况、内存的使用情况、每个进程的占用资源情况等。同时Linux 系统中，每个运行的进程在 /proc 目录下都有一个以 PID 命名的文件夹。通过查看这个文件夹，你可以挖出它的所有信息
```bash
ls -l /proc/1234/cwd # 查看进程 1234 的当前工作目录。
```
### 11、cp
cp指令用于复制文件或目录。  
```bash
cp -r 源路径 目标路径  #最常用，递归复制目录
```

### 12、mv
mv 用于移动或重命名文件/目录  
```bash
mv 源路径 目标路径     # 移动文件或目录
mv old.txt new.txt    # 重命名
```

### 13、mkdir
创建目录  
```bash
mkdir 目录名
mkdir -p a/b/c   # 递归创建多级目录
```

### 14、touch
创建空文件或修改文件时间  
```bash
touch 文件名
```

### 15、cat
查看文件内容（适合小文件）  
```bash
cat 文件路径
```

### 16、more / less
分页查看文件  
```bash
more 文件路径
less 文件路径   # 更强大，支持上下滚动、搜索
```

### 17、head
查看文件开头内容  
```bash
head -n 10 文件路径   # 查看前10行
```

### 18、chmod
修改文件权限  
```bash
chmod 755 文件名
```
说明：
r=4，w=2，x=1  
755 表示：所有者 rwx，组 r-x，其他 r-x  

### 19、chown
修改文件所有者  
```bash
chown 用户名 文件名
chown 用户名:组名 文件名
```

### 20、df
查看磁盘使用情况  
```bash
df -h
```

### 21、du
查看目录占用空间  
```bash
du -h 目录
du -sh 目录   # 总大小
```

### 22、ps
查看进程  
```bash
ps aux
```

### 23、kill
结束进程  
```bash
kill PID
kill -9 PID   # 强制杀死
```

### 24、find
查找文件  
```bash
find 路径 -name "文件名"
```

### 25、which
查找命令路径  
```bash
which ls
```

### 26、whereis
查找命令相关文件  
```bash
whereis ls
```

### 27、uname
查看系统信息  
```bash
uname -a
```

### 28、history
查看历史命令  
```bash
history
```

### 29、clear
清空终端  
```bash
clear
```

### 30、alias
设置命令别名  
```bash
alias ll='ls -l'
```

### 31、tar
打包文件或目录  
```bash
tar -czvf 文件名.tar.gz 目录名
-c	创建新的归档文件
-x	解压归档文件
-t	列出归档内容
-f	指定归档文件名（必须紧跟文件名）
-v	显示详细过程（verbose）
-z	使用 gzip 压缩或解压
-j	使用 bzip2 压缩或解压
-J	使用 xz 压缩或解压
-u	更新归档中的文件
-r	向已有归档追加文件
```

### 32、ip
```bash
ip [选项] 对象 {命令 | help}
对象 (OBJECT)：指定操作的网络资源类型
命令 (COMMAND)：对对象执行的操作，如 show、add、del、set
选项 (OPTIONS)：控制输出或协议族，如 -4 (IPv4)、-6 (IPv6)、-s (统计信息)


link	网络接口管理	ip link show 查看接口；ip link set eth0 up 启动网卡
addr	IP 地址管理	ip addr show 查看地址；ip addr add 192.168.1.10/24 dev eth0 添加地址
route	路由表管理	ip route show 查看路由；ip route add default via 192.168.1.1 添加默认路由
neigh	邻居表 (ARP/ND)	ip neigh show 查看 ARP 表；ip neigh add 192.168.1.20 lladdr 00:11:22:33:44:55 dev eth0 添加静态 ARP
rule	策略路由规则	ip rule show 查看规则；ip rule add from 192.168.1.100 table 100 添加策略路由
netns	网络命名空间	ip netns add testns 创建命名空间；ip netns exec testns bash 进入命名空间
tunnel	隧道管理 (GRE/IPIP)	ip tunnel add tun0 mode gre remote 1.2.3.4 local 5.6.7.8
```

### 33、set
设置环境变量，用于控制脚本的行为，比如常用的如果命令执行失败，脚本是否继续执行。  
```bash
set -x 显示所有命令
set -u 禁止未定义变量
set -e 禁止错误退出
# 常在脚本开头使用如下组合拳
set -euo pipefail
#-e: 命令失败即退出
#-u: 遇到未定义的变量即退出（防止 rm -rf $UNDEFINED_VAR/* 这种由于变量写错导致的误删）。
#-o pipefail: 只要管道中任意一个环节失败，整个管道就被视为失败
```

### 34、pwd
打印当前工作目录  

###

### 常用组合示例

```bash
# 查找日志中包含 error 的行数
cat log.txt | grep "error" | wc -l

# 查看占用内存最多的进程
ps aux | sort -rk 4 | head

# 实时查看日志
tail -f log.txt
```
## Linux指令里面的符号
### 1.&&
前面的指令成功执行完后，接着执行后面的指令。  
### 2.&
在命令末尾加上 &，可以让这个命令在后台运行，一般是在控制终端的时候需要打开某个会持续打印内容的命令的时候需要用到，因为如果不加上 &，这个命令就会一直占用着这个终端，导致我们无法在这个终端上执行其他的命令了。如用iperf3 -s的时候
### 3.|
管道符，前一个命令的输出作为后一个命令的输入。

### 1.重定向符号（I/O 重定向
| 符号          | 用法                 | 说明                                |
| ----------- | ------------------ | --------------------------------- |
| `>`         | `command > file`   | 将命令输出重定向到文件，覆盖原内容                 |
| `>>`        | `command >> file`  | 将命令输出追加到文件末尾                      |
| `<`         | `command < file`   | 将文件内容作为命令输入                       |
| `<<`        | Here Document      | `command <<EOF ... EOF`，将多行文本作为输入 |
| `<<<`       | Here String        | `command <<< "text"`，将字符串作为输入     |
| `2>`        | `command 2> file`  | 将标准错误（stderr）重定向到文件               |
| `2>>`       | `command 2>> file` | 将标准错误追加到文件                        |
| `&>`        | `command &> file`  | 将标准输出和标准错误都重定向到文件                 |
| `>&`        | 文件描述符重定向           | `command >&2` 将标准输出重定向到标准错误       |
| `/dev/null` | 丢弃输出               | `command > /dev/null 2>&1` 丢弃所有输出 |

### 2.管道和命令连接符
| 符号     | 用法                | 说明                            |       |                             |       |                     |
| ------ | ----------------- | ----------------------------- | ----- | --------------------------- | ----- | ------------------- |
| `      | `                 | `cmd1                         | cmd2` | 管道：将 cmd1 的标准输出传给 cmd2 作为输入 |       |                     |
| `      |                   | `                             | `cmd1 |                             | cmd2` | 逻辑或：cmd1 失败时执行 cmd2 |
| `&&`   | `cmd1 && cmd2`    | 逻辑与：cmd1 成功时执行 cmd2           |       |                             |       |                     |
| `;`    | `cmd1; cmd2`      | 顺序执行 cmd1 和 cmd2，无论成功与否       |       |                             |       |                     |
| `&`    | `cmd &`           | 后台执行命令                        |       |                             |       |                     |
| `()`   | `(cmd1; cmd2)`    | 子 Shell 执行命令，命令在子 Shell 中独立执行 |       |                             |       |                     |
| `{}`   | `{ cmd1; cmd2; }` | 命令组合，在当前 Shell 中执行            |       |                             |       |                     |
| `!`    | `! command`       | 逻辑非，取反命令退出状态                  |       |                             |       |                     |
| `time` | `time command`    | 统计命令执行时间（不是符号，但常和管道结合使用）      |       |                             |       |                     |

### 3. 通配符和模式匹配
| 符号       | 用法                | 说明                                  |
| -------- | ----------------- | ----------------------------------- |
| `*`      | `*.txt`           | 匹配任意长度的任意字符                         |
| `?`      | `file?.txt`       | 匹配单个字符                              |
| `[...]`  | `[abc]*`          | 匹配方括号中的任意一个字符                       |
| `[!...]` | `[!a]*`           | 匹配不在方括号中的字符                         |
| `{...}`  | `file{1,2,3}.txt` | 扩展：生成 file1.txt、file2.txt、file3.txt |
| `~`      | `~/`              | 当前用户家目录                             |
| `.`      | `./script.sh`     | 当前目录                                |
| `..`     | `../`             | 上级目录                                |
| `**`     | `**/*.txt`        | （bash 4+）递归匹配子目录                    |
### 4. 变量与参数符号
| 符号       | 用法             | 说明          |
| -------- | -------------- | ----------- |
| `$`      | `$VAR`         | 变量引用        |
| `${}`    | `${VAR}`       | 明确变量边界或高级操作 |
| `$#`     | `echo $#`      | 参数数量        |
| `$?`     | `echo $?`      | 上条命令退出状态    |
| `$0`     | 脚本名            |             |
| `$1..$9` | 位置参数           |             |
| `$@`     | 所有位置参数（逐个展开）   |             |
| `$*`     | 所有位置参数（当作一个整体） |             |
| `$$`     | 当前 Shell PID   |             |
| `$!`     | 最近后台命令的 PID    |             |

### 5. 引号和转义符
| 符号       | 用法              | 说明             |
| -------- | --------------- | -------------- |
| `"`      | `"text $VAR"`   | 双引号，允许变量替换和转义  |
| `'`      | `'text $VAR'`   | 单引号，原样输出，不替换变量 |
| `` ` ``  | `` `command` `` | 命令替换（旧形式）      |
| `$(...)` | `$(command)`    | 命令替换（推荐形式）     |
| `\`      | `\n` 或 `\$VAR`  | 转义字符           |
| `#`      | `# 注释`          | 注释，忽略整行或行尾内容   |
| `:`      | `:`             | 空命令，类似 `true`  |
| `\n`     | 换行              | 在双引号中或命令中换行    |

### 6. 特殊文件符号和测试符号
| 符号        | 用法                       | 说明                         |
| --------- | ------------------------ | -------------------------- |
| `.`       | `.`                      | 当前目录，或者 source 命令 `. file` |
| `/`       | `path/file`              | 目录分隔符                      |
| `-`       | `-f file`                | 测试文件或选项标志                  |
| `[` `]`   | `[ -f file ]`            | 条件测试，必须有空格                 |
| `[[` `]]` | `[[ $a == $b ]]`         | 高级条件测试，支持模式匹配              |
| `-o`      | `[ -f file -o -d dir ]`  | 或逻辑（在 test/[] 中）           |
| `-a`      | `[ -f file -a -r file ]` | 与逻辑（在 test/[] 中）           |

### 7. 作业控制和其他符号
| 符号          | 用法                 | 说明            |
| ----------- | ------------------ | ------------- |
| `%`         | `jobs`, `%1`       | 作业编号          |
| `^`         | `^old^new`         | 快速替换上条命令中的内容  |
| `~+` / `~-` | `cd ~+` / `cd ~-`  | 上次或上上次目录      |
| `=`         | `VAR=value`        | 变量赋值          |
| `export`    | `export VAR=value` | 导出环境变量        |
| `alias`     | `alias ll='ls -l'` | 命令别名          |
| `type`      | `type command`     | 查看命令类型（内建/外部） |




## 打包软件给离线使用
在实际的开发中遇到这种情况，实体机没办法连接到网络，但是需要下载一个工具，因此可以在虚拟机上下载好，然后打包通过终端的scp命令上传到实体机上，以iperf3工具为例。

因为我的虚拟机和实体机是不同的系统，一个是linux一个是arm64，所以后面就选择了在主机pc进行下载包，然后打包给虚拟机了。
1. 进入华为云服务器镜像 https://repo.openeuler.org/
2. 选择适合的版本和架构，下载iperf3的rpm包
3. 通过scp命令将rpm包上传到实体机上，用网线连接虚拟机和实体机，上传命令如下
```bash
scp iperf3-3.1.1-1.aarch64.rpm root@192.168.1.100:/root/
```
4. 在实体机上安装iperf3，其实就是解压安装包
```bash
rpm -ivh iperf3-3.1.1-1.aarch64.rpm
```
5. 验证安装成功
```bash 
iperf3 --version
```
这样就完成了在没有网络的实体机上安装iperf3工具的过程了。在完成这个的时候，我一开始忘记了实体机和虚拟机是不同的系统，所以一开始给实体机上传了个linux的iperf3包，在打包的过程中，我发现原来包核心就包含两个文件，一个是程序本身，另一个是依赖库文件。

## 常用工具
### 1.fzf
fzf是一个快速的模糊查找工具，它可以在命令行中快速查找文件、目录、进程等，主要的使用手段是在终端中按下`Ctrl + R`，然后输入要查找的内容，fzf就会在历史命令中查找匹配的内容，然后再按下回车键就可以直接执行了。
```bash
sudo apt install fzf
```
### 2.top
top是一个实时显示系统运行状态的工具，它可以显示系统的CPU使用率、内存使用率、进程列表等信息，主要的使用手段是在终端中输入`top`命令，然后就可以看到系统的运行状态了。核心使用内容如下
1. 按1键显示每个CPU的使用率
2. 按M键按内存使用率排序
3. 按H键显示线程
4. 按k键杀死进程，输入PID即可
5. 查看某个进程的线程    top -H -p 178912
6. 查看某个用户的进程    top -u root



## 端口
端口是指在计算机网络中，用于标识一个应用程序的端点，它是一个整数，范围从0到65535。每个应用程序都有一个或多个端口，用于接收和发送数据。端口分为三类：
1. 知名端口（Well-known ports）：0-1023，分配
2. 注册端口（Registered ports）：1024-49151，分配
3. 动态/私有端口（Dynamic/Private ports）：49152-65535，未分配
### 1.查看端口占用情况
```bash 
nmap -an # 查看所有端口占用情况，需要安装nmap工具
```

## 环境变量
环境变量是操作系统中用于存储系统配置信息和用户信息的变量，它们可以在命令行或脚本中使用。环境变量通常以大写字母命名，并且可以包含路径、用户名、系统设置等信息。
用env指令来看环境变量，我们主要看的内容是pash和home这两个环境变量，path环境变量是系统用来查找可执行文件的路径列表，而home环境变量则是当前用户的主目录路径。  
在pash中我们可以把需要用到的脚本或者应用程序放进去，这样每次使用就可以随时随地调用了，配置的位置在.bashrc文件中，配置方法如下
```bash
export PATH=$PATH:/path/to/your/script_or_app #一定要加上$PATH:，这是说把原来的路径也保留着，不然就只能访问到这个路径了
source ~/.bashrc # 让修改生效
```

## 调试软件
背景：在开发过程中，遇到打开一个软件后，没办法正常运行，为了查看是哪里报错了，所以需要在linux终端调试，主要有以下方法：
1. ldd ./your_app # 查看依赖的库文件
2. ./your_app # 查看运行时的错误信息
3. ./appPunp -platform eglfs  # 尝试使用 eglfs 平台  
   ./appPunp -platform linuxfb # 或者尝试使用 linuxfb (纯软件渲染，不依赖 GPU)


## 开源代码学习（V0.11）
### 任务调度 / kernel / sched.c
他的大致流程如下：  
用户程序运行  
      ↓  
时钟中断 (do_timer)  
      ↓  
counter--，如果 >0 → 返回继续运行  
      ↓  
counter == 0 → 调用 schedule()  
      ↓  
schedule()：  
  1. 处理信号，唤醒任务  
  2. 找到 counter 最大的 TASK_RUNNING  
  3. 如果都为 0 → 重新计算 counter  
  4. switch_to(next)  
      ↓  
切换到新进程  

调用switch_to()函数切换到新进程，具体动作如下：  
schedule()  
   ↓  
找到 counter 最大的进程 next  
   ↓  
switch_to(next)  
   ↓  
CPU 执行 ljmp → 加载 TSS → 切换上下文  
   ↓  
新进程开始运行  

### GPIO驱动
GPIO驱动中linux中分为用户态和内核态，用户态操作GPIO就是是通过Sysfs（过时）或更推荐的字符设备接口（/dev/gpiochipX），使用libgpiod库提供的命令行工具，操作直观：
```bash
# 设置引脚24为输出，并设置为高电平
gpioset <gpiochip> 24=1
```



# 1.QT学习
## 1.1.QML学习
### 1.1.1.常用操作
1. 在一个界面中使用另一个界面
这种操作有好几种方法如下所示
```qml
//方法一：作为属性声明
property UserCanTest cantest1: UserCanTest{
    canTarget: can1
    send_frame_id: 0x456 
    recv_frame_id: 0x123
}
将组件实例作为属性值，通过属性名访问
//方法二：作为组件声明
GetTestData {
    id: getTestData
}
作为父组件的子元素，通过id访问，作为独立的子组件存在
```
### 1.1.2.组件各种对齐方法
1. text组件类的对齐方法
```
horizontalAlignment左右对齐的可选值
所有上述组件都支持以下相同的对齐值：
对齐值	说明	效果
Text.AlignLeft	左对齐	文本靠左排列（默认值）
Text.AlignRight	右对齐	文本靠右排列
Text.AlignHCenter	水平居中	文本在组件水平方向居中
Text.AlignJustify	两端对齐	文本均匀分布，左右两端对齐（多行文本有效）

verticalAlignment 垂直对齐的可选值：
Text.AlignTop (顶部对齐)
Text.AlignBottom (底部对齐)
Text.AlignVCenter (垂直居中)
```

### 1.1.3.组件在上层显示
组件中上层显示一般是说组件他和父组件生命周期是相同的，这个组件只是被隐藏起来了，需要他显示的时候只需要触发一个事件，但是显示后，这个组件如果是全屏的话，他点击背部还是可以点击到父组件的内容的，所以我们需要做一下处理。  
1. 使用遮罩层
2. 控制父组件的enable属性
3. 在弹出的组件上设置一个全屏的透明背景，捕获点击事件，阻止事件冒泡到父组件，核心用mouseArea捕获点击事件，代码如下

### 1.1.4.Connections使用
A 组件里监听 B 组件抛出的信号时，Connections 就是那根跨越空间的“连线”，Connections 最关键的属性是 target。你把 target 指向谁，你就能接收谁的信号。
```qml
Connections {
    target: 信号发送者 // 这里指向某个对象 ID 或 属性
    
    // 信号处理器命名规则：on + 信号名（首字母大写）
    function onDataChanged() {
            console.log("当前传感器数据已更新")
    }
}
```
属性介绍
```
target	Object	核心属性。指定要监听信号的对象。如果设为 null（默认值），则不监听任何信号。

enabled	bool	控制连接是否处于激活状态。默认为 true。设为 false 时，即使信号触发，处理器也不会执行。

ignoreUnknownSignals	bool	默认为 false。如果设为 true，当 target 中不存在某个 onSignal 处理器对应的信号时，QML 引擎不会报错。
```

### 1.1.5.翻译工具lupdate
lupdate是一个命令行工具，用于从QML文件中提取可翻译的字符串。lupdate的语法如下：
```bash
# 进入你的项目根目录，这里应该包含 UI/ 文件夹（主要有CMakelist.txt）
cd /home/lubancat/work/qt/punp/qt
# 翻译文件更新生成到绝对路径
/opt/Qt/6.8.3/gcc_64/bin/lupdate . -ts /home/lubancat/work/qt/punp/qt/UI/translations/app_zh_CN.ts 
#如果是不同的语言，需要修改ts文件的名称
```
在用的时候需要下载才行，怎么下载自己问ai


## 1.2.C++学习
### 1.2.1.调用系统终端
我们在开发的时候有时候需要在qt中调用终端的指令来直接访问整个系统的功能，在qt中主要有两种方法来使用终端的指令，一种是直接用system函数来调用，另一种是用QProcess类来调用，下面是两种方法的示例代码
```cpp
//方法一：使用system函数
// ❗ 无法获取输出
// ❗ 阻塞线程（UI会卡死）
// ❗ 不安全（容易被注入）
// ❗ 不可控（无法管理进程）
#include <cstdlib>
system("ls -l");

//方法二：使用QProcess类
// 1.启动一个命令（最基本）
QProcess process;
process.start("ls", QStringList() << "-l");
process.waitForFinished();
// 2.获取标准输出（stdout）
QString output = process.readAllStandardOutput();
// 3.获取错误输出（stderr）
QString error = process.readAllStandardError();
// 4.执行复杂 shell 命令（管道 / 重定向）
QProcess process;
process.start("bash", QStringList() << "-c" << "ls -l | grep txt");
process.waitForFinished();
// 5.同步执行（阻塞）
process.waitForFinished();
// 6.异步执行（推荐 ⭐⭐⭐）
QProcess *process = new QProcess(this);
connect(process, &QProcess::readyReadStandardOutput, [=]() {
    qDebug() << process->readAllStandardOutput();
});

connect(process, &QProcess::finished, [=]() {
    qDebug() << "finished";
});
process->start("ping", QStringList() << "www.google.com");
// 7.结束进程
process.terminate(); // 温和结束
process.kill();      // 强制结束

```

## 1.3.配置文件makefile
### 1.3.1.如何实现在开发的时候执行某条语句，在发布的时候不执行
在开发翻译功能的时候发现，我在开发环境时下载了依赖包，但是在执行系统哪里没有这个执行包，因此需要在编译为执行系统的对应执行文件的时候我需要屏蔽掉这个执行包的检测功能，因此我就想在makefile文件中添加一个条件判断，如果是开发环境就执行这个包的检测，如果是发布环境就不执行这个包的检测，下面是示例代码  

方案一：使用自定义开关（最推荐）  
发布环境（默认）： cmake .. （此时不检测 lupdate）  
开发环境： cmake -DBUILD_DEV_MODE=ON ..  
```cmake
# 1. 定义一个开关，默认关闭（OFF 表示发布环境）
option(BUILD_DEV_MODE "Enable development tools like lupdate" OFF)

if(BUILD_DEV_MODE)
    message(STATUS "Development mode: Searching for Linguist tools...")
    find_package(Qt6 REQUIRED COMPONENTS LinguistTools)
    
    # 执行翻译更新逻辑
    qt6_add_translations(your_project TS_FILES your_project_zh.ts)
else()
    message(STATUS "Release mode: Skipping lupdate check.")
    # 如果发布环境不需要更新 .ts，但仍需要把现有的 .ts 编译成 .qm，可以用更轻量的宏
    # 或者直接跳过，只要你的 .qm 已经包含在 .qrc 资源文件中即可
endif()
```
方案二：根据环境变量自动判断  
```cmake
# 检查环境变量 ENV_TYPE 是否为 "development"
if("$ENV{ENV_TYPE}" STREQUAL "development")
    find_package(Qt6 REQUIRED COMPONENTS LinguistTools)
    qt6_add_translations(your_project TS_FILES your_project_zh.ts)
else()
    message(STATUS "Non-development environment detected, skipping lupdate.")
endif()
```
方案三：静默查找（不报错模式）
```cmake
# 不带 REQUIRED，找不到也不会 Error
find_package(Qt6 COMPONENTS LinguistTools QUIET)

# 检查是否真的找到了该目标
if(TARGET Qt6::lupdate)
    message(STATUS "lupdate found, adding translation targets.")
    qt6_add_translations(your_project TS_FILES your_project_zh.ts)
else()
    message(WARNING "lupdate not found, translation update targets will not be created.")
endif()
```
### 1.3.2.资源文件
1. SOURCES：代码的源头
SOURCES（或者在 qt_add_executable 中直接列出的 .cpp 和 .h 文件）是给编译器看的。

处理对象：.cpp、.h、.cxx 等源文件。

处理流程：

编译：编译器将 .cpp 编译成二进制的 .o (或 .obj) 目标文件。

MOC 处理：如果 .h 文件中有 Q_OBJECT 宏，Qt 会自动调用元对象编译器生成 moc_xxx.cpp。

链接：链接器将这些目标文件打包成最终的可执行文件。

如果不写会怎样：会报 undefined reference（未定义的引用）错误，因为链接器找不到代码的实现。

2. RESOURCES：文件的容器
RESOURCES 是给 Qt 资源系统看的。它利用 rcc（Qt Resource Compiler）工具，将外部文件直接嵌入到二进制程序中。

处理对象：.qml、.js、.png、.svg、.json 等非代码文件。

处理流程：

虚拟化：rcc 将这些文件转换成 C++ 数组。

嵌入：这些数据被编译进可执行文件。

访问：在程序运行期间，你可以通过特殊的路径前缀 qrc:/ 或 :/ 访问它们，建议用相对路径来访问。

优点：

路径安全：不需要担心用户删除了外部图片导致程序崩溃，因为文件就在二进制包里。

部署方便：发布程序时，只需要给用户一个 .exe（或 Linux 下的二进制文件），不需要带一堆文件夹。

3. RESOURCES后的路径
RESOURCES 后的路径是相对于资源文件的路径，而不是相对于可执行文件的路径，比如
```cmake
qt_add_resources(appPunpQT "additional_resources"
    PREFIX "/"
    FILES
        users.json
)
```
访问他的路径就是":/users.json"
```cmake
qt_add_resources(appPunpQT "translations"
    PREFIX "/i18n"
    FILES
        "UI/translations/app_zh_CN.qm"
)
```
这个的话就是":/i18n/UI/translations/app_zh_CN.qm"，他包含了资源文件的路径了，所以访问的时候也要包含资源文件的路径了，问题出在Qt 6 资源系统（Qt Resources）在 CMake 中的默认行为：别名（Alias）问题，如果你不想加前缀，那么就使用 BASE 参数，或者直接手动指定别名
```cmake
qt_add_resources(appPunpQT "translations"
    PREFIX "/i18n"
    BASE "UI/translations"  # 忽略这个目录前缀
    FILES
        "UI/translations/app_zh_CN.qm"
        "UI/translations/app_en_US.qm"
)
```
这样就可以不用加上资源文件的路径了，直接访问":/i18n/app_zh_CN.qm"就可以了，很多时候出现资源找不到的问题就是这个的原因。

## 1.4.CMake指令
### 1.4.1.option() 
用来定义一个布尔型的开关变量，默认值为 OFF，在配置阶段由开发者输入，决定某些功能是否启用。 
### 1.4.2.set() 
用来直接设置变量值  
```cmake
set(MY_FLAG ON)
```
### 1.4.3.add_definitions() / target_compile_definitions()  
用来给编译器添加宏定义，常用于条件编译：
```cmake
add_definitions(-DMY_FEATURE_ENABLED)
```
### 1.4.4.add_compile_options() / target_compile_options()  
添加编译器选项，比如优化等级或警告开关
```cmake
add_compile_options(-Wall -O2)
```
### 1.4.5.feature_summary()
配合 option() 使用，可以在配置结束时打印出哪些功能开关被启用或关闭。




---
# 问题集合

## X4测试程序

### 一、虚拟串口modbus通讯验证

> **背景：** modbus的通讯测试因为需要两台设备相互连接，但是如果用两台设备来进行验证，会费时又费力，编译下载一次程序就要花费很长时间，同时使用的程序还是不知道能不能运行起来的程序，因此起初想法是先用虚拟串口来验证通讯，因此就想着去搞虚拟串口，在这里又耗费了很多时间，目前计算下来差不多花了两天时间了才算是在qt上实现了用虚拟串口发送信息，踩过的坑是一个接一个，首先是socat的安装，安装完成后输入指令socat -d -d PTY,link=/tmp/ttyV0,raw,echo=0 PTY,link=/tmp/ttyV1,raw,echo=0，结果显示socat[4397] N PTY is /dev/pts/3，socat[4397] N PTY is /dev/pts/4，这个时候就以为成功了，结果在qt上打开串口的时候却一直提示没有设备，这个时候才发现原来是因为这个指令创建出来的虚拟串口并不是真正意义上的串口，因此去阅读源程序，发现是卡在了C++端写的程序上，上面用了stat来验证这个是否是设备文件，而虚拟串口是检测不出来的，所以后面有阅读资料找到了新的方法来绕过这个，接着绕过后又卡在了明明发送了为什么没有数据读取出来，又调试了半条才知道是权限问题，即权限太低没办法往这个串口里写数据，最后才算是成功的验证了有数据发送出去，现在是想同时开两个QT程序，一个执行主机程序，一个执行从机程序，但是现在是开的两个qt程序都是执行的是同一个程序，明明都不在同一个目录下，且文件里面的程序确实不同，但是打开的却是同一个程序，现在就卡在这里，找问题，是什么原因导致的呢。

### 二、解决方案
> <span style="color: #5bfaff;">📅2026-03-20 16:00:00</span>  
> **背景**：卡在modbus通讯不上时间过久，启动步骤记录如下  
> <span style="color: #5bfaff;">📅2026-03-23 11:24:22</span>   
> 发送数据echo -e -n "\x01\x03\x00\x00\x00\x0a\xc5\xcd" > /tmp/vpts1，无反应   
> 下一步验证，检查QT程序是否成功接收到了数据   
> <span style="color: #5bfaff;">📅2026-03-23 13:53:34</span>   
> 在C++中启动Debug模式，用Libmodbus 库自带的modbus_set_debug(this->ctx, TRUE);   
> <span style="color: #5bfaff;">📅2026-03-23 14:14:07</span>   
> 往虚拟串口发送数据，输出区域没有反应，问题可能出现在以下几种情况：modbus没有启动；串口没有接收到数据；数据格式错误；接收到了没有打印出来，现在开始逐一排查问题  
> <span style="color: #5bfaff;">📅2026-03-23 14:36:23</span>  
> modbus没有启动被排除,串口没有接收到数据被排除,现在怀疑是数据格式错误，因为报错CRC不对，怀疑没有成功接收完整的数据，因此调整“字符间超时”和在接收前清空缓存，使得数据包完整  
> <span style="color: #5bfaff;">📅2026-03-23 15:16:53</span>   
> 调整后，数据格式错误被排除，因为调整后没有成功，现在开始怀疑是modbus没有设置为从机的原因，因为这程序上我没有看到设置成从机的代码，因此就怀疑是这个原因导致的，现在开始验证是否  
> <span style="color: #5bfaff;">📅2026-03-23 15:32:53</span>  
> 终于定位到了问题所在，是因为在C++中没有设置modbus的从机模式，所以根本就没用用到接收函数，导致没有数据被接收出来，因此就导致了没有反应。

### 三、复盘反思
> **复盘**:  
> 一开始的需求是完成modbus的测试功能，但是思索了一会后发现如下问题:1.没有例子可以参考；2.不清楚项目是如何使用modbus的；3.不太清楚modbus的通讯协议；因此我第一步是想着找个例子来参考，于是联系了后端的开发人员，他跟我说了在哪里已经写好了，并且指导了我如何使用，告知我只一台机器调用这个函数，另一台机器调用另一个函数即可，我因为想着早点完成任务，不愿意去仔细分析和读懂程序，所以想着懂得怎么用即可，于是就直接准备开始测试程序，其实在使用的过程中也在了解着程序，但是只停留在读懂了程序是怎么运行的，于是就想着去用了，而不知道程序为什么要这样用，导致了后续难以进展，我觉得这就是主要原因，归根到底还是不愿意花时间去深入学习，而想着急于看到成果，这只是原因之一，因为在用程序的过程中，我后知后觉才发现，原来我需要做的任务，不是简单一个界面，而是需要两个界面的相互配合，并且需要两台设备来做测试，这时我存在以下麻烦需要解决：1、供电线不足；2、两台设备物理上和软件上如何连接；3、实机测试一次大概要耗费一个小时，因此我想着用虚拟仿真来代替，所以后面就转去了学习如何在linux上启动虚拟串口，在启动好串口后，我又遇到了以下问题：1、对QT程序使用虚拟串口一点经验都无；2、没看过C++端的modbus程序；3、不清楚如何去调试虚拟串口，于是下一步我又去学习，读懂了程序，学会了如何使用虚拟串口，清楚如何发送数据到串口上和查看接收到的十六进制数据，但是卡在了QT程序无法使用虚拟串口的问题上，这一卡就是几天时间，首先我用的时候只改了设备地址，但是调试输出显示找不到设备，于是我从以下角度去解决这个问题：1、找不到设备是因为找到了打不开，还是因为根本就没找到；2、是不是libmodbus库不支持虚拟串口的时候（有次问AI,AI说的不支持）；于是我在对应的目录下用ls查看目录是否存在，发现存在就排除了设备文件不存在的问题，后面让ai辅助修改程序，发现了是权限存在问题，于是我就根据ai的提示去改文件的权限和在socat上就提前用好权限，后面不知道怎么的，确实是成功的让QT程序可以发送信号到虚拟串口上了，于是我就肯定了问题所在就是权限的问题，但是那时候没有注意到数据的格式其实是混乱的，根本不是我想要得到的数据，然后那时候我就启动了两个进程来执行QT程序，一个QT执行从机程序，一个QT执行主机程序测试一下是否可以行得通，一折腾，发现根本没效果，这时候我发现了以下几个大问题：1、QT程序执行的是同一个程序，明明已经复制到了别的地方，目录都不同；2、数据又发送不出去了，又找不到设备文件了。这时候我又耗费了好长一段时间去找为什么两个qt程序会是一样的原因，找了好久又没找到，然后我就转去看数据为什么没有发送成功上，又卡在了找不到设备文件上，这时候就已经产生了放弃使用虚拟串口的准备，打算直接实机测试，因为这时候已经耗费了接近两天的时间了，害怕自己是在一条错误的方向上一直走下去，觉得及时止损才是最好的处理方法，于是我放弃了使用虚拟串口，去使用实机测试，然后就动手连接实机，烧录程序耗费了一个小时，然后绝望的发现根本没有通讯成功，这时候试过一次烧录两台设备后，根本就不愿意再试一次，所以当天下午就立案了，决定要好好记录每一个步骤，以防再出现毫无头绪，像个无头苍蝇一样撞来撞去的结果。最终使用科学的方法，把问题拆开，按不同的角度分析，然后逐个排查验证，终于解决了问题。  
> 
>**反思**:    
> 1.对modbus不熟悉，没有从机概念，所以动手前应该先熟悉目标  
> 2.对出现的问题，没有一套系统的解决方法论，导致在解决问题时，没有一个统一的流程，导致问题的解决效率低。  
> 3.对不熟悉的技术，学习不够  
> 
>**总结**:    
> 1.在解决问题时，应该先熟悉目标和熟悉技术，再解决问题    
> 2.遇到问题时，把问题记录下来，罗列出问题的原因，一一去排查  







# QT开发软件功能

## 一、构建配置

通常包含 Debug、Release 和 Profile 三个默认选项。

Debug (调试模式)： 编译时不进行优化，包含完整的调试符号，方便在代码报错时定位行号。生成的可执行文件体积较大。

Release (发布模式)： 进行代码优化（如运行速度优化、体积压缩），不包含调试信息。用于最终交付给用户的版本。

Profile (分析模式)： 介于两者之间，通常是开启优化的 Release 版本，但保留了用于性能分析（如耗时统计）的符号。

## 二、构建目录

功能： 指定编译生成的中间文件（.obj, .o）和最终程序（.exe）存放的位置。

Shadow Build (影子构建)： 默认开启。它将编译产物放在源码文件夹之外的一个独立目录中。这非常有用，可以保持源代码目录的整洁，并且允许同一个项目同时拥有多个平台的构建产物而不产生冲突。

## 三、构建步骤

qmake / CMake 步骤： * 详情： 这是“预编译”阶段。如果是 qmake，它会处理 .pro 文件生成 Makefile；如果是 CMake，它会处理 CMakeLists.txt。

额外参数 (Additional arguments)： 你可以在这里输入自定义宏，例如 CONFIG+=debug_and_release。

Make 步骤： * 调用编译器（如 MSVC 的 nmake 或 GCC 的 make）进行真正的代码编译。

并行操作 (-j)： 如果你的电脑核心数多，可以在这里设置类似 -j8 的参数来加速编译。

## 四、清理步骤

功能： 定义点击“清理 (Clean)”项目时执行的操作。

作用： 通常是删除构建目录下的所有生成文件。当你遇到一些奇怪的编译错误（比如修改了头文件但编译器没反应）时，执行“清理”并“重新构建”是万能神药。

## 五、构建环境

功能： 设置编译时使用的系统环境变量。

关键点： * 它默认继承系统环境变量（PATH）。

如果你使用了第三方库（如 OpenCV 或第三方驱动），但不想把它们配进系统全局变量，你可以在这里点击 “Details” 手动添加它们的路径。这样编译时就能找到对应的 .h 和 .lib 文件了。

## 六、C++ 设置 (C++ Settings / Compiler flags)
如果你使用的是特定版本的 C++（如 C++17 或 C++20），有时需要在这里确认编译器开关是否正确开启。

## 七、QT如何处理资源文件
在QT6.8资源的打包机制已经从传统的“手动配置 .qrc 文件”全面转向了以 CMake 为核心的自动化流程，核心工具是RCC(Resource Compiler)，无论是qml文件还是json文件都经过RCC处理，生成对应的头文件，他的核心过程是rcc 读取文件 生成包含十六进制数据的 .cpp 文件  编译器将其编译为 .obj/.o 链接进主程序。那么他们的文件地址在执行的时候只哪呢，运行期间，Qt 会在内存中维护一个以 :/ 开头的虚拟文件系统，通过 QFile 或 URL 即可像访问普通路径一样访问这些内置数据。  

1. qml文件:  在QT6中，qml文件不再是简单的资源文件，而是被视为模块，在cmakelist中这样定义
```
qt_add_qml_module(appmyapp
    URI MyModule
    VERSION 1.0
    QML_FILES
        Main.qml
        SideBar.qml
)
```
这样定义后，在程序编译的时候就会自动打包所有的 QML_FILES 会被自动加入资源系统（默认路径通常是 :/qt/qml/MyModule/）。Qt 6.8 的 QML Compiler (qmlcachegen) 会在编译阶段将 QML 源代码转化为字节码，甚至是真正的 C++ 代码，这种方式提供了更好的语法检查和性能优化，而不仅仅是把文本存进去。
2. json文件等资源:  json文件如果需要被打包成资源文件，可以直接在cmakelist中这样定义
```
qt_add_resources(appmyapp "configs"
    PREFIX "/data" # 资源访问路径前缀
    FILES
        "settings.json"
        "theme.json"
)
```
rcc 默认会检查文件，如果压缩后体积能缩小（默认阈值 70%），则会使用 zstd 或 zlib 进行压缩存储，运行时会自动解压缩，访问路径为 :/data/settings.json。对于一些小文件（如图标、配置文件等），Qt 6.8 的资源系统会自动启用压缩机制，以节省内存和磁盘空间。同时一定要记得JSON 文件在程序中是只读的，如果需要修改，必须先把它读出来，修改后再写回去。




---
# 常用操作
## 一、项目烧录前板程序
```bash
#arm64架构编译
1.虚拟机上挂载好主机的共享路径，获得目的文件
sudo vmhgfs-fuse .host:/ /mnt/hgfs/ -o allow_other -o nonempty #添加最后面的参数可以挂载到非空目录下
2.使用docker进入容器
sudo docker run --privileged -v /mnt/hgfs/WinShare/qt:/root -it terra-arm64-qt6-build-addmd:v2 bash    
进入后如果ls没有想要的内容，那么就cp root 进入root目录下，内容就都在里面了
3.添加环境变量
  export PATH=/usr/bin/qt6/bin:$PATH
  export LANG=C.UTF-8
  export LC_ALL=C.UTF-8
4.使用cmake编译cmake文件
mkdir build 创建一个文件夹
cd build/ 进入这个文件夹
然后编译目标文件
cmake .. (因为目标文件在上一层)
5.使用make -j8（只有8内核）

#下载进去
1.前板通电并用网线接上电脑
2.打开通讯工具，链接上目标id
3.停止进程的使用
cd root
cd /userdata
./manage-myapp.sh stop
4.把在虚拟机中生成的build文件里面的appPunp改名移进前板的文件中，替代掉可执行文件
如果那个工具打不开则在终端用这个指令
scp D:\WinShare\qt\build\appPunp root@192.168.168.122:/userdata/app/
#如果显示已经保存有旧的文件了，则用下面这条语句删掉
ssh-keygen -R 192.168.168.122
5.重新打开进程
 ./manage-myapp.sh start 
```

## 二、window挂载linux目录
工具使用：WinFsp + SSHFS-Win（github上都有下载）  
下载地址：https://github.com/winfsp  
使用方法：我的做法是打开资源管理器，点击地址栏，输入
```bash
#.r 代表以当前登录用户身份运行，通常能解决 80% 的权限拒绝问题
\\sshfs.r\用户名@服务器IP\home\用户名
```

## 三、其他应用识别当前电脑的IP为梯子IP
cursor举例：在clash软件中，开启全局模式，将所有流量都通过梯子路由，这样就可以了，同时还要在cursor的网络设置中，把http2.2改为用http1.1

## 四、linux上重启网络IP
```bash
sudo systemctl restart NetworkManager # 重启网络管理器
sudo dhclient -v ens36
```

# GIT常用操作

## 一、提交代码
```bash
git add .
git commit -m "提交信息"
git push origin 分支名
```

## 二、拉取代码
```bash
git clone ssh://github.com/用户名/仓库名.git #克隆仓库
git pull origin 分支名 #更新代码
git reset --hard #重置到最新提交，删除所有未提交的更改，才可以重新拉取代码
```

## 三、版本回退
```bash
git reset --hard 提交ID #回退到指定提交
```

## 四、上传文件.gitignore
在项目根目录下创建一个名为 .gitignore 的文件，并在其中添加规则来指定哪些文件或目录应该被 Git 忽略不上传到git仓库。例如：
```
*.qm  // 忽略所有qm文件
!UI/translations/*.qm  // 但是保留UI/translations目录下的qm文件，因为这些文件是翻译文件，不能被忽略
```
# 工作日记
## 每日工作总结

## 每时工作细则
> <span style="color: #5bfaff;">📅2026-03-24 09:22:05</span>  
> 启动两个不同的QT程序，让他们相互通讯  
> <span style="color: #5bfaff;">📅2026-03-24 10:10:32</span>   
> 存在以下大问题：复制出来的工程打开后里面的文件始终指向原文件，没办法执行两个程序  
> 出发角度：1、查找资料找到问题所在；2、尝试用不同的仓库来模拟两个程序，先运行一个，然后切换仓库再运行一个  
> 执行计划：因为时间较紧迫，先选择角度二，不行再从角度一出发  
> <span style="color: #5bfaff;">📅2026-03-24 11:21:49</span>   
> 角度二可以实现，在socat中成功看到了两组数据的相互传输，但是qt页面上成功次数没有发生变化  
> 怀疑：没有成功触发handleResponse，因为失败次数也没增加，所以肯定没有进这个函数  
> 下一步：阅读源程序梳理出触发handleResponse的条件  
> <span style="color: #5bfaff;">📅2026-03-24 13:35:51</span>   
> 触发handleResponse ⬅ 触发信号SendFinished ⬅ 进入函数dealSendInThread，而函数dealSendInThread的触发则是当modbus对应的线程中存储区中有内容时才触发。需要详细去读懂user_modbus_deal函数。  
> <span style="color: #5bfaff;">📅2026-03-24 15:49:51</span>  
> 终于定位到问题了，数据没问题而是触发了信号，但是没有执行槽函数，所以没有下一步操作  
> <span style="color: #5bfaff;">📅2026-03-24 16:09:05</span>  
> 终于疏通信号了，给的程序真的坑死人，不一步步梳理根本发现不了，燃尽了，问题在两个地方，一个是触发信号了，但是<span style="color: #f12d2d;">没有执行槽函数</span>，一个是执行成功和失败的增减前有个jb判断语句，直接跳出去了。原因在于源程序中使用的槽函数是旧版本的格式，新版本不支持所以就根本没有执行这个槽函数，同时Connect格式也不对用<span style="color: #f12d2d;">target: target</span>  有问题，经过测试发现这种写法没办法绑定成功，要target: mb2这样写明。但是之前的一直用旧版本槽函数格式，也没见有问题，所以这个问题我觉得有争议，但是没时间验证了，余着先。  
> <span style="color: #5bfaff;">📅2026-03-25 10:25:12</span>  
> 完成了modbus的测试方案编写，现在准备开始编码  
> <span style="color: #5bfaff;">📅2026-03-25 10:51:15</span>  
> 下一步：写主机端让主机每1s发送一次数据，先实现失败次数可以和发送次数同步增加，因为之前的成功次数加上失败次数不等于发送次数，所以要排查问题。  
> <span style="color: #5bfaff;">📅2026-03-25 11:08:10</span>  
> 下一步：建立三对的虚拟串口，然后实现通讯次数的同步刷新  
> <span style="color: #5bfaff;">📅2026-03-25 11:43:57</span>  
> 下一步：实现三对的串口通讯，然后实现通讯次数的同步刷新  
> <span style="color: #5bfaff;">📅2026-03-25 13:26:46</span>  
> 下一步：编写完整的modbus测试程序，实现三对的串口通讯，然后实现通讯次数的同步刷新。程序大致如下，主机端每0.5s三路modbus发读数据，总次数加一，从机如果接收到并且响应，则成功次数加一，否则失败次数加一。  
> <span style="color: #5bfaff;">📅2026-03-25 16:27:14</span>  
> 终于实机测试通过了  
> <span style="color: #5bfaff;">📅2026-03-25 16:27:55</span>  
> 学习CAN通讯，熟悉CAN的C++部分内容  
> <span style="color: #5bfaff;">📅2026-03-26 08:59:57</span>  
> 学习CAN通讯  
> <span style="color: #5bfaff;">📅2026-03-26 10:33:20</span>  
> CAN在QT程序中实现，就是用socat的套接字来实现CAN的通讯。  
> 下一步：测试后端工程师给的CAN通讯程序是否正常运行。  
> <span style="color: #5bfaff;">📅2026-03-26 15:14:39</span>  
> 下一步：编写CAN的QT程序测试方案的xmind  
> <span style="color: #5bfaff;">📅2026-03-26 16:07:58</span>  
> 下一步：编写CAN测试的UI显示程序  
> <span style="color: #5bfaff;">📅2026-03-30 10:02:23</span>  
> 真的服了，合并git分支搞半天，之前写的通讯那边的一直都没有更新，导致合并起来很麻烦。  
> 下一步：写好CAN的应用封装，只输出我需要的CAN通讯总次数，成功次数，失败次数  


# 编程能力
## 1 编程思想
### 1.1 解耦思想
在这次开发过程中，我深刻体会到了代码解耦的重要性，在前半段开发过程中，我的代码都是写在一起的，功能模块之间没有明显的界限，这样就导致了代码的可读性和可维护性都非常差，尤其是对于从后板读取过来的值是直接存贮在全局变量中的，然后在其他qml文件中就直接调用了这个全局变量，导致在后期调试以及维护时，非常的乏力且耗费时间，修改一个变量的值就会动好多地方，如果要换个变量，那就更耗费时间了，所以深刻理解了解耦的重要性，在后半段开发过程中，就特别有意开始避免这种代码耦合的情况，尽可能的把代码按模块分开，做到每个文件尽可能的独立，功能单一，这样就大大提高了代码的可读性和可维护性，同时也方便了后续的调试和维护工作。
#### 1.1.1 解耦的手段
1. 模块化设计：把不同的功能模块分开，每个模块负责一个特定的功能，这样就可以避免不同功能之间的耦合。
2. 接口设计：通过定义清晰的接口来实现模块之间的通信，这样就可以避免模块之间的直接依赖。
3. 事件驱动：通过事件来触发不同模块之间的交互，这样就可以避免模块之间的直接调用。
4. 使用设计模式：比如观察者模式、工厂模式等，这些设计模式可以帮助我们实现代码的解耦，提高代码的灵活性和可维护性。
5. 使用依赖注入：通过依赖注入来管理模块之间的依赖关系性。
6. 使用消息队列
7. 使用事件总线
8. 使用中间件

#### 1.1.2 我的解耦经验
1. 少用全局变量，如果要用全局变量，也要尽量把它封装在一个模块中，其他模块通过接口来访问这个全局变量，这样就可以避免全局变量的滥用，如在qml绑定参数的时候，全局变量不可用进入代码的内部，只能通过qml自己的变量来绑定，这样改动的时候，不需要再去看程序里面的代码了，直接在qml的变量定义哪里改就好了。
2. 在qml中使用信号槽来实现模块之间的通信，这样就可以避免模块之间的直接调用，同时也方便了后续的调试和维护工作，不要做qml文件中，直接调用另一个qml文件的函数，而是要通过触发信号来实现模块之间的通讯。


### 1.2 架构设计思想
架构设计思想是指在软件开发过程中，如何设计软件的整体结构和组织，这工作是在软件开发的早期阶段，由软件架构师来完成的。

### 1.3 分层思想
在做软件或驱动开发的时候，肯定是先给软件进行整体的架构分析，然后根据架构分析，把软件进行分层设计，每个层负责一个特定的功能，这样就可以避免不同功能之间的耦合，同时也方便后续的调试和维护工作，我个人的核心思想是，分层最好按照行业标准来实现因为统一，<span style="color: #f12d2d;">同时切记下层的接口永远不可以调用上层的接口</span>  ，这是检验分层设计是否合理的一个重要标准，如果下层的接口调用了上层的接口，那么就说明这个分层设计是有问题的，需要重新设计一下分层的结构了。

# 通讯协议

## 1.1 modbus协议

### 1.1.1 modbus协议简介
Modbus 是一种应用于工业自动化的应用层报文传输协议，主要用于主站（Master/Client）与从站（Slave/Server）之间的数据交换。它在物理层支持 RS-485/232 串口（RTU/ASCII 模式）和以太网（TCP 模式），具备半双工通信特性。其核心是将工业设备的数据抽象为四种基本表：线圈（Coils）、离散输入（Discrete Inputs）、保持寄存器（Holding Registers）和输入寄存器（Input Registers）。该协议以报文格式简单、协议栈开销小、部署灵活而著称，是目前工业控制领域兼容性最广、最通用的通信标准。
### 1.1.2 modbus协议的实现
实现 Modbus 协议是一个从底层硬件驱动到高层数据解析的系统工程。首先，需要构建物理层通信接口，如配置串口波特率、校验位或建立 TCP 监听服务。其次，需定义数据映射模型，将程序中的业务变量与 Modbus 地址空间挂钩，并严格处理大端字节序（Big-Endian）转换。在核心逻辑层，必须实现报文的封装与拆解（ADU/PDU）：主站负责按功能码组帧并处理超时重发，从站负责断帧识别、地址校验及功能码解析。此外，必须包含一套完备的校验与异常处理机制，通过 CRC 循环冗余校验确保数据完整性，并针对非法地址或操作返回标准异常码。为了保证系统的实时性，通常采用非阻塞状态机模式来驱动发送与接收流程，从而确保在多设备组网环境下通信的高效与稳定。。

