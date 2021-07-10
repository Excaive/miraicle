<div align="center">

# miraicle

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/miraicle)
![PyPI](https://img.shields.io/pypi/v/miraicle?color=brightgreen)
![PyPI - License](https://img.shields.io/pypi/l/miraicle?color=orange)

一个基于 mirai-api-http 的轻量级 Python SDK

</div>

## 安装

``` bash
pip install miraicle
```

## 示例

``` python
import miraicle


@miraicle.Mirai.receiver('GroupMessage')
def hello_to_group(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    bot.send_group_msg(group=msg.group, msg='Hello world!')


@miraicle.Mirai.receiver('FriendMessage')
def hello_to_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    bot.send_friend_msg(qq=msg.sender, msg='Hello world!')


qq = 123456789              # 你登录的机器人 QQ 号
verify_key = 'miraicle'     # 你在 setting.yml 中设置的 verifyKey
port = 8080                 # 你在 setting.yml 中设置的 port (http)

bot = miraicle.Mirai(qq=qq, verify_key=verify_key, port=port)
bot.run()
```

如果你想获得更多信息，可以查阅 `miraicle` 的 [文档](https://excaive.github.io/miraicle/)。
