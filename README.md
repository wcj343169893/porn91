# 打卡系统自动打卡

## Action 自动签到

使用GitHub提供的CI任务，可以实现定时自动签到。

步骤：

1. Fork 本项目
3. 打开项目设置，在`Secrets and Variables`，点 New repository secret，添加变量名`username`，`password`，并填入账号密码，
4. 保存后就可去Action里面触发任务。

## 如何安装
创建虚拟目录
```shell
python -m venv venv
```
安装依赖
```shell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

安装浏览器
```shell
sudo npx -y playwright install-deps
python -m playwright install

```


``` shell
pip install --upgrade -r requirements.txt
```

## 使用说明

查看帮助
``` shell
$ python -m daka -h
```

usage: -m [-h]  [-q | -v] [username] [password] [from_email] [email_password] [to_email] [max_page] [upload_url] [oss_key_id] [oss_access_key] [oss_bucket_name] [oss_uid]

打卡系统自动打卡

positional arguments:
    username     账号
    password     密码
    from_email    
    email_password
    to_email
    max_page
    upload_url
    oss_key_id
    oss_access_key
    oss_bucket_name
    oss_uid


options:
  -h, --help   show this help message and exit
  -q           安静模式，不显示运行信息
  -v           详细模式，显示更多运行信息


