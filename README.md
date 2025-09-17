# 打卡系统自动打卡

## Action 自动签到

使用GitHub提供的CI任务，可以实现定时自动签到。

步骤：

1. Fork 本项目
3. 打开项目设置，在`Secrets and Variables`，点 New repository secret，添加变量名`username`，`password`，并填入打卡的账号密码，
4. 保存后就可去Action里面触发任务。

## 如何安装
创建虚拟目录
```shell
python -m venv venv
```
安装依赖

```shell
pip install -r requirements.txt
```


``` shell
pip install --user daka
```
``` shell
pip install  daka
```
```shell
pip install daka --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org
```
查看版本
```shell
pip show daka
```


```
pip install --upgrade -r requirements.txt
```

## 使用说明

``` shell
#查看帮助
$ python -m daka -h

usage: -m [-h]  [-q | -v] [username] [password] [appid] [appsecret]

打卡系统自动打卡

positional arguments:
    username     打卡账号
    password     打卡密码
    appid        roleApi的appid
    appsecret    roleApi的appsecret

options:
  -h, --help   show this help message and exit
  -q           安静模式，不显示运行信息
  -v           详细模式，显示更多运行信息
```

