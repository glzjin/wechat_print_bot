from sqlobject import StringCol, SQLObject, ForeignKey, sqlhub, connectionForURI, mysql, IntCol, TinyIntCol, TimestampCol
import buu_config

class class_model(object):

    MySQLConnection = mysql.builder()
    sqlhub.processConnection =  MySQLConnection(user = buu_config.config.mysql_username, password = buu_config.config.mysql_password,
                                                host = buu_config.config.mysql_addr, db = buu_config.config.mysql_database)

    class User(SQLObject):
        userName = StringCol()

    class Printer(SQLObject):
        printer_type = TinyIntCol()
        printer_value = StringCol()
        printer_name = StringCol()
        user = ForeignKey('User')

    class PrintJob(SQLObject):
        page_num = IntCol()
        file_name = StringCol()
        user = ForeignKey('User')
        printer = ForeignKey('Printer')
        timestamp = TimestampCol()

    def init():
        if not sqlhub.processConnection.tableExists('user'):
            class_model.User.createTable()

        if not sqlhub.processConnection.tableExists('printer'):
            class_model.Printer.createTable()

        if not sqlhub.processConnection.tableExists('print_job'):
            class_model.PrintJob.createTable()
