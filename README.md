# TeleGraphSpider

本项目为使用 python3 编写的 TeleGraph 爬虫工具。

## 使用
本项目可以使用直接使用 .py 文件（需要安装 Python3 并添加到环境变量），或使用 Releases 的 exe 文件。

所需文件如下：

- 程序主体：TeleGraphSpider.py / TeleGraphSpider.exe
- url 列表文件

### url 列表文件要求

url 列表文件需要使用 UTF-8 Without BOM 编码，一行一个网址，网址的形式如下:

```
https://telegra.ph/XXXXX
```

### 使用源码

拖动 url 列表文件件到 TeleGraphSpider.py

直接运行的情况，将会读取当前文件夹下的 urls.txt

在当前目录运行：

```shell
python TeleGraphSpider.py
```

#### 打包 exe 文件

可使用 pyinstaller 包，用如下命令将会在 `./dist/` 目录下创建 windows 可执行程序：

```shell
pyinstaller -F --icon=icon.ico TeleGraphSpider.py
```

### 使用封装版

拖动 url 列表文件到  TeleGraphSpider.exe

直接运行的情况，将会读取当前文件夹下的 urls.txt

## 输出

若正常运行后将会在当前文件夹创建 telegraph_lib 文件夹。

url 列表文件中每个 url 会按照标题在 telegraph_lib 文件夹中创建文件夹，每个 url 中的图片将被下载到该文件夹中。