# 打卡系统自动打卡

## Action 自动签到

使用GitHub提供的CI任务，可以实现定时自动签到。

步骤：

1. Fork 本项目
2. 申请[rollApi](https://mp.weixin.qq.com/s/UvKr0SG73_Py63ICUnLBPw)的账号
3. 打开项目设置，在`Secrets and Variables`，点 New repository secret，添加变量名`username`，`password`，并填入打卡的账号密码，
   `appid`，`appsecret`填写roleApi的应用信息。
4. 保存后就可去Action里面触发任务。

## 如何安装

``` shell
pip install --user daka
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

