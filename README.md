# 目录
[项目介绍](#项目介绍)

图像文字识别流程介绍[查看ppt介绍](readmedir/文字识别学习分享.md)

使用演示[查看文章](readmedir/使用演示.md)

[开发环境](#开发环境)

[设计模块和应用](#设计模块和应用)

[打包过程](#打包过程)

[打包过程内容](#打包过程内容)

[环境搭建步骤](#环境搭建步骤)

## 项目介绍
该项目是一个用python实现的截图文字识别的工具，实现流程代码并不多；其包含两个模块，打包模块、应用模块；

打包模块介绍：一键制作安装程序exe流程模块，该模块使用Inno Setup 6实现。（但因为文件上传限制未将该应用相关文件上传）

打包模块流程：1.开发环境commit代码；2.生产环境执行脚本一键打包；（拉取最新代码->执行打包命令->生产工具安装程序exe）3.用户下载安装程序，执行并安装；

应用模块介绍：识别用户截图中的文字，供用户复制粘贴；

应用模块流程：1.用户打开应用；2.选择识别方式（百度api\本地OCR）；3.通过应用截取包含文字的图片；4.应用根据选择的方式最图片进行处理；



## 开发环境

windows10
Python 3.6.0
pip 20.2.4
svn 1.13.0

## 设计模块和应用

### python

altgraph                  0.17
baidu-aip                 2.2.18.0
certifi                   2020.11.8
cffi                      1.14.3
chardet                   3.0.4
cryptography              3.2.1
cycler                    0.10.0
future                    0.18.2
idna                      2.10
kiwisolver                1.3.1
matplotlib                3.3.2
numpy                     1.19.4
opencv-python             4.4.0.46
pefile                    2019.4.18
Pillow                    8.0.1
pip                       20.2.4
pycparser                 2.20
pyinstaller               4.0
pyinstaller-hooks-contrib 2020.10
pyparsing                 2.4.7
pyperclip                 1.8.1
pypiwin32                 223
pytesseract               0.3.6
python-dateutil           2.8.1
pywin32                   228
pywin32-ctypes            0.2.0
requests                  2.25.0
scipy                     1.5.4
setuptools                28.8.0
six                       1.15.0
tesserocr                 2.4.0
urllib3                   1.26.2
win32core                 221.36
win32gui                  221.6

### 应用

Inno Setup 6.1.2
tesseract v5.0.0-alpha.20200328

## 文件列表说明

```
+---Inno Setup 6					：打包应用目录
|	+---ISCC.exe					：主程序
+---log					  			 ：打包日志输出目录
+---src								：源码目录
|	+---build						：编译目录
|	+---dist 						：exe生成目录
|	+---pytesseract					：修改后的python模块
|	+---setup						：安装包生成目录
|	|	+---keyi-rtis-setup.exe			：安装包
|	+---Tesseract-OCR				：OCR应用目录
|	|	+---tessdata				：语言数据文件
|	|	+---tesseract.exe			：主程序
|	+---config.ini					：百度OCR配置文件
|	+---logo.ico					：logo图片
|	+---noteshrink.py				：图像中间处理
|	+---screen_ocr.py				：程序执行目录
+---config.ini						：百度OCR配置文件
+---installer.bat					：打包脚本
+---KEYI-RTIS.iss					：Inno打包应用配置脚本
+---setup.bat						：打包脚本启动
+---start-svnserver.bat			：svn server启动脚本
```

## 打包过程

1. 运行start-svnserver.bat脚本启动svn服务器
2. 开发提交更新代码
3. 运行setup.bat脚本执行打包过程，等待打包完成
4. 打包成功，通知开发
5. 开发拉取安装程序src\setup\keyi-rtis-setup.exe
6. 运行安装程序生产测试生产安装包

## 打包过程内容

1. 更新源码文件src
2. 删除上次打包文件目录dist\KEYI-RTIS
3. 执行exe打包命令pyinstaller
4. 删除上次安装包
5. 运行iscc执行KEYI-RTIS.iss脚本文件
6. 提交打包好的安装包keyi-rtis-setup.exe

### * 执行百度OCR需要在安装目录下的config.ini文件中设置百度ocr应用信息

## 文档DOC

打包工具：https://www.pyinstaller.org

Tesseract应用文档：https://tesseract-ocr.github.io

窗口程序文档：https://www.runoob.com/python/python-gui-tkinter.html

Opencv文档：https://docs.opencv.org/master/d6/d00/tutorial_py_root.html

## 优秀博客

https://www.mayi888.com/archives/60604

https://www.python-course.eu/tkinter_canvas.php

## 附：资源下载链接

百度通用文字识别：https://ai.baidu.com/tech/ocr/general（找到快速学习文档）

innosetup应用下载：https://mlaan2.home.xs4all.nl/ispack/innosetup-6.1.2.exe

tesseract-ocr下载：https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.0.0-alpha.20200328.exe

tessdata下载：https://codeload.github.com/tesseract-ocr/tessdata/zip/master

## 环境搭建步骤

1. 将"发布环境"目录放到E:\repos下

2. 下载Tesseract-ocr安装程序，安装之后将应用目录"Tesseract-OCR"放到src目录下

3. 下载innosetup安装程序，安装之后将应用目录放到"发布环境"目录下

4. pip install pyinstaller

5. pip install baidu-aip

6. 进入src目录执行screen_ocr.py（python screen_ocr.py），如果报缺少模块，则按照提示安装模块

   例如：

   PIL=>pip install Pillow

   pip install pyperclip

   win32*=>pip install pypiwin32

7. 成功执行screen_ocr.py之后，开始测试打包，进入"发布环境"目录执行setup.bat，执行失败检查以上步骤（报"xxx路径不存在"错误可忽略）

8. 安装svn

9. 在reops下创建keyi-rtis目录

10. 在keyi-rtis下右键将建库

11. 在src目录下checkout

