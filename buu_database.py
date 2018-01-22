import redis
import buu_config, buu_model
from buu_model import class_model
import datetime

class class_database_op(object):

    def __init__(self):
        self.config = buu_config.config
        self.redis_ins = redis.Redis(host = self.config.redis_addr, port = self.config.redir_port,  \
                                    db = self.config.redis_db, password = self.config.redis_password)

    def flush_redis(self):
        self.redis_ins.flushdb()

    def put_user(self, userName):
        exist_userId = self.redis_ins.get('user-username-id-' + userName)
        if not exist_userId:
            exist_user = class_model.User(userName = userName)
            userId = exist_user.id
            self.redis_ins.set('user-id-username-' + str(userId), userName)
            self.redis_ins.set('user-username-id-' + userName, userId)
            return int(userId)
        else:
            return exist_userId

    def update_user(self, userName, userId):
        userId = int(userId)

        if self.redis_ins.get('user-id-username-' + str(userId)):
            if str(self.redis_ins.get('user-id-username-' + str(userId)).decode('utf-8')) == userName and \
                int(self.redis_ins.get('user-username-id-' + userName)) == userId:
                return None

        try:
            exist_user = class_model.User.select(class_model.User.q.id == userId).limit(1).getOne()
            exist_user.set(userName = userName)
            self.redis_ins.set('user-id-username-' + str(userId), userName)
            self.redis_ins.set('user-username-id-' + userName, userId)
            return None
        except Exception:
            exist_user = class_model.User(userName = userName)
            userId = exist_user.id
            self.redis_ins.set('user-id-username-' + str(userId), userName)
            self.redis_ins.set('user-username-id-' + userName, userId)
            return int(userId)

    def get_username_by_id(self, userId):
        userId = int(userId)
        exist_userName = self.redis_ins.get('user-id-username-' + str(userId))
        if exist_userName:
            return exist_userName.decode('utf-8')

        try:
            exist_user = class_model.User.select(class_model.User.q.id == int(userId)).limit(1).getOne()
            self.redis_ins.set('user-id-username-' + str(userId), exist_user.userName)
            self.redis_ins.set('user-username-id-' + exist_user.userName, userId)
            return exist_user.userName
        except Exception:
            return None

    def get_user_by_id(self, userId):
        try:
            exist_user = class_model.User.select(class_model.User.q.id == int(userId)).limit(1).getOne()
            return exist_user
        except Exception:
            return None


    def get_id_by_username(self, userName):
        exist_userId = self.redis_ins.get('user-username-id-' + userName)
        if exist_userId:
            return exist_userId

        try:
            exist_user = class_model.User.select(class_model.User.q.userName == userName).limit(1).getOne()
            userId = exist_user.id
            self.redis_ins.set('user-id-username-' + str(userId), userName)
            self.redis_ins.set('user-username-id-' + userName, userId)
            return userId
        except Exception:
            return None

    def get_user_current_step(self, userId):
        step = self.redis_ins.get('step-' + str(userId))
        if step:
            return step.decode('utf-8')

        return '0'

    def set_user_current_step(self, userId, step):
        self.redis_ins.set('step-' + str(userId), step)

    def step_back(self, userId):
        for single_key in self.config.fail_clean:
            self.delete_redis_kv(userId, single_key)
        cur_step = self.get_user_current_step(userId)
        stop_pos = cur_step.rfind('-')
        if stop_pos != -1:
            cur_step = cur_step[:stop_pos]
        else:
            cur_step = '0'
        self.set_user_current_step(userId, cur_step)

    def set_redis_kv(self, userId, key, value):
        self.redis_ins.set('custom-' + str(userId) + '-' + str(key), value)

    def get_redis_kv(self, userId, key):
        return self.redis_ins.get('custom-' + str(userId) + '-' + str(key))

    def delete_redis_kv(self, userId, key):
        self.redis_ins.delete('custom-' + str(userId) + '-' + str(key))



    def add_printer_info(self, userId, printer_name, printer_type, printer_value):
        try:
            class_model.Printer(printer_type = printer_type, printer_name = printer_name, printer_value = printer_value, user = self.get_user_by_id(userId))
        except Exception:
            pass

    def get_my_printers(self, userId):
        try:
            exist_printers = class_model.Printer.select(class_model.Printer.q.user == self.get_user_by_id(userId))
            return exist_printers
        except Exception:
            return None

    def delete_my_printer(self, userId, printerId):
        try:
            exist_printer = class_model.Printer.select((class_model.Printer.q.user == self.get_user_by_id(userId)) & (class_model.Printer.q.id == printerId)).limit(1).getOne()
            class_model.Printer.delete(exist_printer.id)
            return True
        except Exception:
            return False

    def get_all_printers(self, userId):
        try:
            exist_printers = class_model.Printer.select()
            return exist_printers
        except Exception:
            return None

    def get_printer(self, printerId):
        try:
            exist_printer = class_model.Printer.select(class_model.Printer.q.id == printerId).limit(1).getOne()
            return exist_printer
        except Exception:
            return None

    def add_print_job(self, page_num, file_name, user, printer):
        try:
            job = class_model.PrintJob(page_num = page_num, file_name = file_name, user = user, printer = printer, timestamp = datetime.datetime.now())
            return job.id
        except Exception:
            return None

    def get_print_job_total(self, printerId):
        try:
            return int(class_model.PrintJob.select(class_model.Printer.q.id == printerId).sum('page_num')) * self.config.print_price
        except Exception:
            return 0
