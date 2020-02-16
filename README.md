# bangbot
基于adb的简单音游bot	

适用于"BanG Dream! Girl's Band Party!"

#### 准备工作

1. 启用usb调试
   设置->关于手机 点击版本号7次 进入开发者模式
   选择“返回”就可以看到“开发者选项”的菜单 进入“开发者选项” 打开USB调试
   
2. 获取adb
   下载 [android platform tools (科学上网)](https://dl.google.com/android/repository/platform-tools-latest-windows.zip) 或 [minimal adb and fastboot](https://androidmtk.com/download-minimal-adb-and-fastboot-tool)
   
3. 把adb目录添加到系统PATH

4. 安装[python(3.6+)](https://www.python.org/downloads/)

5. [下载](https://res.ayachan.best/bangbot/bangbot.zip) 或 `git clone https://github.com/12f23eddde/bangbot`

#### 录制

`python3 record.py -t <文件名>`

录制的时候会提示按Enter开始

按Enter之后要直接开始打歌

在打歌之前按键位的话对结果有影响

最后按Enter结束并保存到文件

#### 打歌

`python3 replay.py -t <文件名> -o <时间调整(ms)>`

打歌的时候会延时3秒自动开始（可用-d参数调整）

您需要先按第一串键 （第一串键从第一个note开始，释放时间与下一个键的间隔时间超过release_offset， 可用-r参数调整）

可按Enter提前中止

#### 华为设备适配

由于较新的华为设备 (EMUI 8+) 更改了touchevent的实现，之前的代码可能无法在这些设备上工作。

在这些设备上，请使用以下命令

`python3 replay.py -t <文件名> -o <时间调整(ms)> --huawei`

#### 其它设备支持

由于安卓10 (Android Q) 更改了安全机制，无root权限的设备无法使用replay.py。

理论上安卓版本6-9 (API Level 23-28) 都可正常使用。

当前已经在以下设备上测试通过：

小米8青春版 三星S6 Edge 华为M3 荣耀V30 华为P20