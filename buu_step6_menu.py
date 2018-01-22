import buu_database
import buu_config
import request_utils
import itchat
import utils
import time

class class_step(object):

    def __init__(self):
        self.step_dict = [  \
                            (None, None), \
                            (self.print_job_add, None), \
                            (self.add_printer, None), \
                            (self.printer_manager, None), \
                            (self.printer_total, None)
                        ]
        self.config = buu_config.config
        self.class_database_op = buu_database.class_database_op()
        self.allow_ext = ['.doc', '.docx', '.pdf']

    def add_printer(self, msg, userId):
        current_type = self.class_database_op.get_redis_kv(userId, 'printer_current_type')
        if not current_type:
            if not self.class_database_op.get_redis_kv(userId, 'inputing'):
                self.class_database_op.set_redis_kv(userId, 'inputing', 1)
                return '请选择您打印机的连接类型，1为Google Cloud Printer（开发中）, 2为 Epson Connect Email.'
            else:
                self.class_database_op.delete_redis_kv(userId, 'inputing')
                if msg.text == '1':
                    self.class_database_op.step_back(userId)
                    return '当前此类型还未完成，已返回上级菜单。'
                elif msg.text == '2':
                    self.class_database_op.set_redis_kv(userId, 'printer_current_type', msg.text)
                    return '现在，请输入您打印机的 email .'

        current_value = self.class_database_op.get_redis_kv(userId, 'printer_current_value')
        if not current_value:
            self.class_database_op.set_redis_kv(userId, 'printer_current_value', msg.text)
            return '现在，请输入您打印机的名称.'

        current_name = msg.text

        current_value = current_value.decode('utf-8')
        current_type = int(current_type)
        self.class_database_op.add_printer_info(userId, current_name, current_type, current_value)

        self.class_database_op.delete_redis_kv(userId, 'printer_current_value')
        self.class_database_op.delete_redis_kv(userId, 'printer_current_type')
        self.class_database_op.delete_redis_kv(userId, 'inputing')

        self.class_database_op.step_back(userId)

        return '系统已经保存您所输入的数据。'

    def printer_manager(self, msg, userId):
        if not self.class_database_op.get_redis_kv(userId, 'inputing'):
            self.class_database_op.set_redis_kv(userId, 'inputing', 1)
            return_str = '以下是您所拥有的打印机。\nID 名称\n'
            results = self.class_database_op.get_my_printers(userId)
            for printer in results:
                return_str += str(printer.id) + " " + printer.printer_name + "\n"
            return_str += "输入0返回上级，输入ID则删除打印机。"
            return return_str
        else:
            self.class_database_op.delete_redis_kv(userId, 'inputing')
            self.class_database_op.step_back(userId)

            if msg.text == '0':
                self.class_database_op.step_back(userId)
                return "已经返回上级菜单。"
            else:
                printer_id = int(msg.text)
                if self.class_database_op.delete_my_printer(userId, printer_id):
                    return "打印机删除成功。"
                else:
                    return "打印机删除失败。"

    def printer_total(self, msg, userId):
        self.class_database_op.step_back(userId)
        return_str = '以下是您所拥有的打印机。\nID |名称 |总收益（元）\n'
        results = self.class_database_op.get_my_printers(userId)
        for printer in results:
            return_str += str(printer.id) + " |" + printer.printer_name + " |" + str(self.class_database_op.get_print_job_total(printer.id)) + "\n"
        return return_str

    def print_job_add(self, msg, userId, msg_opt = None):
        printer_id = self.class_database_op.get_redis_kv(userId, 'current_printer_id')
        if not printer_id:
            if not self.class_database_op.get_redis_kv(userId, 'inputing'):
                self.class_database_op.set_redis_kv(userId, 'inputing', 1)
                return_str = '以下是您可访问的打印机。\nID |名称\n'
                results = self.class_database_op.get_all_printers(userId)
                for printer in results:
                    return_str += str(printer.id) + " |" + printer.printer_name + "\n"
                return_str += "输入0返回上级，输入ID则使用该台打印机。"
                return return_str
            else:
                self.class_database_op.get_redis_kv(userId, 'inputing')

                if msg.text == '0':
                    self.class_database_op.step_back(userId)
                    return "已经返回上级菜单。"
                else:
                    printer_id = int(msg.text)
                    if not self.class_database_op.get_printer(printer_id):
                        self.class_database_op.step_back(userId)
                        return "打印机不存在，已经返回上级菜单。"
                    self.class_database_op.set_redis_kv(userId, 'current_printer_id', printer_id)
                    return "请输入打印份数~"

        amount = self.class_database_op.get_redis_kv(userId, 'print_amount')
        if not amount:
            self.class_database_op.get_redis_kv(userId, 'inputing')

            if msg.text == '0':
                self.class_database_op.step_back(userId)
                return "已经返回上级菜单。"
            else:
                amount = int(msg.text)
                self.class_database_op.set_redis_kv(userId, 'print_amount', amount)
                return "请将您要打印的文件发一个给我，多个文件请多次发送，目前仅支持 .pdf（推荐，务必先解密），doc 和 docx（转换时间稍微久一些） \n"

        amount = int(amount)
        print_file_name = self.class_database_op.get_redis_kv(userId, 'current_print_file_name')
        print_page_count = self.class_database_op.get_redis_kv(userId, 'current_print_file_page_count')
        print_price = self.class_database_op.get_redis_kv(userId, 'current_print_file_print_price')
        create_time = self.class_database_op.get_redis_kv(userId, 'current_print_create_time')
        printer = self.class_database_op.get_printer(int(printer_id))

        if self.class_database_op.get_redis_kv(userId, 'in_processing_file'):
            return '请不要操作，目前还在处理文件。'

        if not print_file_name or not print_page_count or not print_price or not create_time:
            if not msg_opt:
                self.class_database_op.step_back(userId)
                return '操作错误，请发送文件!已经取消当前操作。'
            if 'file_name' not in msg_opt:
                self.class_database_op.step_back(userId)
                return '操作错误，请发送文件!已经取消当前操作。'

            itchat.send_msg("已收到文件,正在处理...", msg['FromUserName'])
            self.class_database_op.set_redis_kv(userId, 'in_processing_file', 1)
            results = utils.doc_get_page_num("cache/files/" + msg_opt['file_name'], msg_opt['file_ext'])
            self.class_database_op.delete_redis_kv(userId, 'in_processing_file')
            print_price = round(self.config.print_price * results[0] * amount, 2)

            itchat.send_msg("每份页数：%d，共打印 %d 份，以下是打印预览。继续打印请转账 %.2f 元，不打印请回复0。" % (results[0], amount, print_price), msg['FromUserName'])
            itchat.send_file(results[1], msg['FromUserName'])

            self.class_database_op.set_redis_kv(userId, 'current_print_file_name', results[1])
            self.class_database_op.set_redis_kv(userId, 'current_print_file_page_count', results[0])
            self.class_database_op.set_redis_kv(userId, 'current_print_file_print_price', print_price)
            self.class_database_op.set_redis_kv(userId, 'current_print_create_time', int(time.time()))

            return

        print_price = float(print_price)
        create_time = int(create_time)
        print_page_count = int(print_page_count)

        if msg.text == '0':
            self.class_database_op.step_back(userId)
            return "已经取消。"
        else:
            if 'money' not in msg_opt:
                self.class_database_op.step_back(userId)
                return "请转账。已经取消当前操作。"

            if create_time >= msg_opt['create_time']:
                self.class_database_op.step_back(userId)
                return "检测到交易重放，已返回上级菜单，请勿重发转账消息。"
            itchat.send_msg("收到转账：%.2f元。时间戳：%d" % (msg_opt['money'], msg_opt['create_time']), msg['FromUserName'])

            print_price = print_price - float(msg_opt['money'])
            create_time = int(time.time())

        self.class_database_op.set_redis_kv(userId, 'current_print_file_print_price', print_price)
        self.class_database_op.set_redis_kv(userId, 'current_print_create_time', int(time.time()))
        if print_price > 0:
            return "金额不足，请继续转账 %.2f 元。" % (print_price)


        self.class_database_op.step_back(userId)

        request_utils_ins = request_utils.request_utils()
        for i in range(0, amount):
            request_utils_ins.send_email(print_file_name, printer)

        print_file_name = print_file_name.decode('utf-8')
        user = self.class_database_op.get_user_by_id(userId)
        self.class_database_op.add_print_job(amount * print_page_count, print_file_name, user, printer)


        return "任务创建成功，请您到打印机那取打印好的资料。"

    def step_tips(self, msg, userId):
        return  '1 - 我要打印\n' \
                '2 - 添加打印机\n' \
                '3 - 管理我的打印机\n' \
                '4 - 查看我的收益\n' \
                '其他输入 - 返回首页'
