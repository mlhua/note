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

## 二、 物理接口与电平特性
1.差分信号接口CAN 必须使用 CAN_H 和 CAN_L 两根线。  
显性电平（Dominant, 逻辑 0）： $V_{diff} = V_H - V_L \approx 2.0V$。此时驱动器强行拉开电位。  
隐性电平（Recessive, 逻辑 1）： $V_{diff} \approx 0V$。此时驱动器高阻态，靠 120Ω 终端电阻回弹。

2.常见物理接口
DB9 接口： 标准工业接口（Pin 2 为 L，Pin 7 为 H）。  
端子排： 常见的工业模块接口（H, L, GND）。  
收发器芯片： 如 TJA1042, SN65HVD230。它负责将 MCU 的 TTL 电平（TX/RX）转换为总线的差分电平。  

## 三、 协议帧结构（Standard CAN 2.0A 为例）
一个完整的 CAN 数据帧包含 7 个部分：  
1.SOF (Start of Frame)： 1 bit 显性电平。  
2.Arbitration Field (仲裁域)： 11 bit ID + RTR 位（远程帧标志）。ID 越小电平 0 越多，优先级越高。  
3.Control Field (控制域)： 包含 IDE（扩展标志）、保留位和 DLC（数据长度码，0-8 字节）。  
4.Data Field (数据域)： 0 到 8 字节的实际负载。  
5.CRC Field (校验域)： 15 bit CRC 序列 + 1 bit 界定符。  
6.ACK Field (应答域)： 发送方发 1（隐性），接收方如果收到必须回填 0（显性）。  
7.EOF (End of Frame)： 7 bit 连续隐性电平，表示结束。  



 # 指令合集
 ## Linux指令
 ### 常用
 ssh 用户名@IP地址
 
### 1、LS
```bash
ls -l #长格式显示：权限、所有者、大小、修改时间等
ls -a #显示所有文件，包括隐藏文件
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


---
# 常用操作
## 一、烧录前板程序
```bash
#arm64架构编译
1.虚拟机上挂载好主机的共享路径，获得目的文件
sudo vmhgfs-fuse .host:/ /mnt/hgfs/ -o allow_other -o nonempty #添加最后面的参数可以挂载到非空目录下
2.使用docker进入容器
sudo docker run --privileged -v /mnt/hgfs/WinShare/qt:/root -it terra-arm64-qt6-build-addmd:v2 bash
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

