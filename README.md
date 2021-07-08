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

你可以使用 [mirai-console-loader](https://github.com/iTXTech/mirai-console-loader) ，它会对 `mirai-console` 进行一键启动和自动更新。安装好 `mirai-api-http` 之后，将 `mirai-api-http` 的 `setting.yml` 模板复制粘贴到配置文件里，并自己设置一个 `verifyKey` 和 `port`。

> `mirai-api-http` 目前已经更新到 `2.x` 版本，这与 `1.x` 版本相比有不少变动。`miraicle` 仅支持 `2.x` 版本的 `mirai-api-http` ，请检查你的 `mirai-api-http` 版本是否正确。

## 开始使用

首先启动 `mirai-console` 并登陆你的机器人账号。你可以查看 [mirai-console](https://github.com/mamoe/mirai-console) 的文档，或者在 `mirai-console` 中输入 `/help` 来学习如何使用。

现在一切工作已经准备完成，你可以开始动手写自己的 bot 了。打开你最熟悉的编辑器或 IDE ，创建一个名为 `bot.py` 的文件，内容如下：

```Python
import miraicle


@miraicle.Mirai.receiver('GroupMessage')
def hello_to_group(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    bot.send_group_msg(group=msg.group, msg='Hello world!')


@miraicle.Mirai.receiver('FriendMessage')
def hello_to_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    bot.send_friend_msg(qq=msg.sender, msg='Hello world!')


qq = 123456789              # 你登陆的机器人 qq 号
verify_key = 'miraicle'     # 你在 setting.yml 中设置的 verifyKey
port = 8080                 # 你在 setting.yml 中设置的 port (http)

bot = miraicle.Mirai(qq=qq, verify_key=verify_key, port=port)
bot.run()
```

修改变量 `qq` 、`verify_key` 和 `port` 的值，然后运行。如果你的设置是正确的，程序会输出类似于这样的内容：

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

## 发生了什么

让我们回来再看上面的这个例子。首先，我们导入了 `miraicle` 包。接着，我们定义了 `hello_to_group` 和 `hello_to_friend` 这两个函数，并使用装饰器 `@miraicle.Mirai.receiver` 来分别修饰它们。注意到，虽然修饰两个函数的装饰器是相同的，但是带了不同的参数。

以 `hello_to_group` 函数为例，当函数被装饰器 `@miraicle.Mirai.receiver` 修饰的时候，`miraicle` 会把这个函数注册到参数 `GroupMessage` 对应的接收器列表。当 `miraicle` 从 `mirai-api-http` 接收到一条类型为 `GroupMessage` 的消息链时，它会首先对消息链进行预处理，封装成 `miraicle.GroupMessage` 对象。然后，`miraicle` 会依次调用 `GroupMessage` 接收器列表中的函数，传入 bot 对象和消息对象。

在 `hello_to_group` 函数中，我们让 bot 对象执行了 `send_group_msg` 方法，这是让 bot 发送一条群消息。`group` 参数代表群号，我们把它赋值为接收到消息的群号；`msg` 参数代表要发送的消息内容，我们传入字符串 'Hello world!'。这样，每当 bot 收到 `GroupMessage` 类型的消息链时，它都会发送 'Hello world!' 作为回应。

类似地，`hello_to_friend` 函数的装饰器参数为 `FriendMessage`，当 bot 接收到好友消息时，它会调用这个函数。

> `miraicle` 支持的消息链类型包括 `GroupMessage`、`FriendMessage` 和 `TempMessage`，分别代表群消息、好友消息和群临时消息，`miraicle` 会把消息链封装成对应的对象。除此之外，你还可以在 `receiver` 的参数中填写各种 [事件类型](https://github.com/project-mirai/mirai-api-http/blob/master/docs/api/EventType.md) ，不过，对于大多数事件类型，`miraicle` 没有对它们进行封装，传入的消息对象是个 `dict`。

## 消息链

我们已经成功地让 bot 发送文字消息。那么，如何让 bot 发送带有表情、图片的更加复杂的消息呢？看完本节之后，你会得到答案。

可能你注意到了，上一节中已经提到了“消息链”这个名词。在 `mirai` 的设计中，消息不是一串字符，而是由文字、表情、图片等消息元素组成的列表。

`miraicle` 也沿用了这样的设计。你可以使用 `msg.chain` 来访问消息对象对应的消息链，它是一个装有各种消息元素的列表，这些消息元素均继承自 `Element`。

当你让 bot 发送消息时，也可以构造一个这样的列表。让我们来把上一节中的 `hello_to_group` 函数改写一下：

```Python
@miraicle.Mirai.receiver('GroupMessage')
def hello_to_group(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    bot.send_group_msg(group=msg.group, msg=[miraicle.Plain('Hello world!'),
                                             miraicle.Face().from_face_id(74),
                                             miraicle.At(qq=msg.sender)])
```

运行程序，现在当你发送一条群消息之后，bot 会发送带有表情的 'Hello world!' ，并 at 你。

下面对各种消息元素进行介绍，你可以使用这些消息元素，构造更加复杂的消息链。

### 文字 (Plain)

TODO

### At

TODO

### At 全体成员 (AtAll)

TODO

### 表情 (Face)

TODO

### 图片 (Image)

TODO

### 闪照 (FlashImage)

TODO

### 语音 (Voice)

TODO

### Xml

TODO

### Json

TODO

### App

TODO

### Poke

TODO

### 骰子 (Dice)

TODO

### 文件 (File)

TODO

## 编写插件

TODO

## 使用过滤器

TODO

## 添加计划任务

TODO
