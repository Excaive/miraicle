<div align="center">

# miraicle

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/miraicle)
![PyPI](https://img.shields.io/pypi/v/miraicle?color=brightgreen)
![PyPI - License](https://img.shields.io/pypi/l/miraicle?color=orange)

一个基于 mirai-api-http 的 Python SDK

</div>

## 安装
`pip install miraicle`

## 准备
`miraicle` 是基于 [mirai-api-http](https://github.com/project-mirai/mirai-api-http) 的，`mirai-api-http` 又是 `mirai-console` 的一个插件。在使用 `miraicle` 之前，请按照 `mirai-api-http` 的文档进行环境搭建和插件配置。

你可以使用 [mirai-console-loader](https://github.com/iTXTech/mirai-console-loader) ，它可以对 `mirai-console` 进行一键启动和自动更新。安装好 `mirai-api-http` 之后，将 `mirai-api-http` 的 `setting.yml` 模板复制粘贴到配置文件里，并自己设置一个 `verifyKey` 和 `port`。

> `mirai-api-http` 目前已经更新到 `2.x` 版本，这与 `1.x` 版本相比有不少变动。`miraicle` 仅支持 `2.x` 版本的 `mirai-api-http` ，请检查你的 `mirai-api-http` 版本是否正确。

## 开始使用
首先启动 `mirai-console` 并登陆你的机器人账号。你可以查看 [mirai-console](https://github.com/mamoe/mirai-console) 的文档，或者在 `mirai-console` 中输入 `/help` 来学习如何使用。

现在一切工作已经准备完成，你可以开始动手写自己的 bot 了。打开你最熟悉的编辑器或 IDE ，创建一个名为 `bot.py` 的文件，内容如下：

```Python
import miraicle


@miraicle.Mirai.receiver('FriendMessage')
def hello_to_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    bot.send_friend_msg(qq=msg.sender, msg='Hello world!')


@miraicle.Mirai.receiver('GroupMessage')
def hello_to_group(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    bot.send_group_msg(group=msg.group, msg='Hello world!')


qq = 123456789          # 你登陆的机器人 qq 号
verify_key = 'miraicle' # 你在 setting.yml 中设置的 verifyKey
port = 8080             # 你在 setting.yml 中设置的 port (http)

bot = miraicle.Mirai(qq=qq, verify_key=verify_key, port=port)
bot.run()
```

修改变量 `qq` 、`verify_key` 和 `port` 的值，然后运行。如果你的设置是正确的，你会看到程序输出类似这样的内容：

```
method '__http_verify' has called
sessionKey: KT26iQBo
method '__http_bind' has called
method '__http_main_loop' starts
```

打开一个 qq 群，随便发送一条消息（前提是你的 bot 也在这个群）；或者向 bot 私发一条消息（前提是你已经添加 bot 为好友）。不出意外的话，你会收到 bot 的回复：

```
Hello world!
```

好的，现在可以祝贺，你的 bot 运行成功了！
