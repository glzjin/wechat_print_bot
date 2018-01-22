import itchat

import utils, os
import buu_config
import buu_msg_handle
import buu_database
import sys
import buu_model
import buu_thread_read_remark

@itchat.msg_register(itchat.content.ATTACHMENT, isGroupChat=False)
def download_files(msg):
    filename, file_extension = os.path.splitext(msg.fileName)
    real_file_name = utils.randomword(32) + file_extension
    msg.download("cache/files/" + real_file_name)
    msg_handler.msg_handle(msg, {'file_name': real_file_name, 'file_ext': file_extension})

@itchat.msg_register(itchat.content.TEXT, isGroupChat=False)
def text_reply(msg):
    msg_handler.msg_handle(msg)

@itchat.msg_register('Note')
def get_note(msg):
    if any(s in msg.text for s in ('转账')):
        import re
        money = round(float(re.compile(r'转账(.*?)元').findall(msg.text)[0]), 2)
        create_time = int(re.compile(r'<begintransfertime><!\[CDATA\[(.*?)\]\]></begintransfertime>').findall(msg['Content'])[0])
        msg_handler.msg_handle(msg, {'money': money, 'create_time': create_time})

@itchat.msg_register(itchat.content.FRIENDS)
def add_friend(msg):
    itchat.add_friend(**msg['Text']) # 该操作会自动将新好友的消息录入，不需要重载通讯录
    itchat.send_msg("欢迎~对我说话来获取菜单吧~", msg['RecommendInfo']['UserName'])

def encrypt_passwords():
    import buu_model, buu_database
    database_op = buu_database.class_database_op()
    exist_cards = buu_model.class_model.Card.select()

    for card in exist_cards:
        print("正在处理... ID:%d" %(card.user.id))
        database_op.save_card_info(card.user.id, card.user_name, card.password)

def exit_callback():
    itchat.auto_login(enableCmdQR=2, hotReload=True, exitCallback=exit_callback)
    itchat.run()

buu_model.class_model.init()

msg_handler = buu_msg_handle.class_msg_handle()

itchat.auto_login(enableCmdQR=2, hotReload=True, exitCallback=exit_callback)

class_database_op = buu_database.class_database_op()
class_database_op.flush_redis()

buu_thread_read_remark.class_init_thread()

# encrypt_passwords()

itchat.run()
