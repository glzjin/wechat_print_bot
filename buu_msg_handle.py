import buu_config, buu_command_dict, buu_database
import itchat
from concurrent.futures import ThreadPoolExecutor

class class_msg_handle(object):

    def msg_handle(self, msg, msg_opt = None):
        self.thread_pool.submit(self.msg_handle_task, msg, msg_opt)
        return

    def __init__(self):
        self.class_database_op = buu_database.class_database_op()

        self.config = buu_config.config
        self.command_dict_class = buu_command_dict.class_command_dict()
        self.command_dict = self.command_dict_class.command_dict

        self.thread_pool = ThreadPoolExecutor(max_workers = 10)

    def msg_handle_task(self, msg, msg_opt):
        user = itchat.search_friends(userName = msg['FromUserName'])

        user_id = None
        if user.get('RemarkName'):
            user_id = int(user.get('RemarkName'))
            new_user_id = self.class_database_op.update_user(msg['FromUserName'], user_id)
            if new_user_id:
                itchat.set_alias(msg['FromUserName'], str(user_id))
                user_id = new_user_id
        else:
            user_id = self.class_database_op.put_user(msg['FromUserName'])
            itchat.set_alias(msg['FromUserName'], str(user_id))

        print('%s: %s' % (msg['FromUserName'], msg.text))
        return_str = self.command_dict_class.step_process(msg, user_id, msg_opt)
        if return_str:
            itchat.send_msg(return_str, msg['FromUserName'])
