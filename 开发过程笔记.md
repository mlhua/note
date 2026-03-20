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
 # 指令合集

 ## Linux指令
 ### 常用
 ssh 用户名@IP地址
 

---
# 问题集合

## X4测试程序

### 一、虚拟串口modbus通讯验证

> **背景：** modbus的通讯测试因为需要两台设备相互连接，但是如果用两台设备来进行验证，会费时又费力，编译下载一次程序就要花费很长时间，同时使用的程序还是不知道能不能运行起来的程序，因此起初想法是先用虚拟串口来验证通讯，因此就想着去搞虚拟串口，在这里又耗费了很多时间，目前计算下来差不多花了两天时间了才算是在qt上实现了用虚拟串口发送信息，踩过的坑是一个接一个，首先是socat的安装，安装完成后输入指令socat -d -d PTY,link=/tmp/ttyV0,raw,echo=0 PTY,link=/tmp/ttyV1,raw,echo=0，结果显示socat[4397] N PTY is /dev/pts/3，socat[4397] N PTY is /dev/pts/4，这个时候就以为成功了，结果在qt上打开串口的时候却一直提示没有设备，这个时候才发现原来是因为这个指令创建出来的虚拟串口并不是真正意义上的串口，因此去阅读源程序，发现是卡在了C++端写的程序上，上面用了stat来验证这个是否是设备文件，而虚拟串口是检测不出来的，所以后面有阅读资料找到了新的方法来绕过这个，接着绕过后又卡在了明明发送了为什么没有数据读取出来，又调试了半条才知道是权限问题，即权限太低没办法往这个串口里写数据，最后才算是成功的验证了有数据发送出去，现在是想同时开两个QT程序，一个执行主机程序，一个执行从机程序，但是现在是开的两个qt程序都是执行的是同一个程序，明明都不在同一个目录下，且文件里面的程序确实不同，但是打开的却是同一个程序，现在就卡在这里，找问题，是什么原因导致的呢。

### 二、解决方案
> <span style="color: #5bfaff;">📅2026-03-20 16:00:00</span>  
> 
> **背景**：需要完成两台屏幕之间的 modbus 通讯验证，现在使用实体调用写好的 test 程序来验证通讯后，无法达到预期效果，同时也使用了虚拟串口来验证通讯，但是卡在 qt 程序没办法成功使用虚拟串口，没法验证通讯。  
> 
> **现状**：头脑一片空白，需要时间整理一下思路，制定一个解决方案来解决这个问题。  
> 
> **下一步计划**：罗列几个方向，然后思考选择哪个方向来解决这个问题  
> 
> **计划执行**：解决QT无法使用虚拟串口的问题  
> 

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
5.重新打开进程
 ./manage-myapp.sh start 
```