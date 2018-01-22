import threading
import itchat
import buu_model, buu_database, request_utils

class MainThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        friends = itchat.get_friends(True)

        for friend in friends:
            try:
                if friend.RemarkName:
                    user_id = int(friend.RemarkName)
                    new_user_id = class_database_op.update_user(friend.UserName, user_id)
                    if new_user_id:
                        itchat.set_alias(friend.UserName, str(user_id))
                        user_id = new_user_id
                else:
                    user_id = self.class_database_op.put_user(friend.UserName)
                    itchat.set_alias(friend.UserName, str(user_id))
            except:
                pass

        database_op = buu_database.class_database_op()

class class_init_thread(object):
    def __init__(self):
        t = MainThread()
        t.start()
