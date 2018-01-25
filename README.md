# 微信打印机器人

## 要求

- python3
- clouconvert([https://cloudconvert.com/](https://cloudconvert.com/))的 api
- 一台支持 EpsonConnect([https://www.epsonconnect.com/](https://www.epsonconnect.com/https://www.epsonconnect.com/))或者 Google cloud print (暂时没做- -)的打印机

## 部署

```
git clone https://github.com/glzjin/wechat_print_bot.git
cd wechat_print_bot
pip install -r requirements.txt
```

## 配置

```
cp buu_config.py.example buu_config.py
vi buu_config.py
```

## 运行

```
python buu.py
```

## 使用

1. 扫码登录
2. 用其他微信号加这个号为好友，随便发句话来获取菜单。

## 感谢

- itchat([https://github.com/littlecodersh/ItChat/](https://github.com/littlecodersh/ItChat/))
