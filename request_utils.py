import buu_config, buu_database
import utils
import io

class request_utils(object):
    def __init__(self):
        self.config = buu_config.config

    def send_email(self, file_name, printer):
        destination = ['glzjin@zhaojin97.cn', printer.printer_value]

        text_subtype = 'plain'


        content="""\
        Test message
        """

        subject="打印"

        from os.path import basename

        from smtplib import SMTP_SSL as SMTP

        from email.mime.multipart import MIMEMultipart
        from email.mime.application import MIMEApplication
        from email.mime.text import MIMEText
        from email.utils import COMMASPACE, formatdate

        try:
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From']   = self.config.smtp_sender
            msg['To'] = COMMASPACE.join(destination)
            msg['Date'] = formatdate(localtime=True)
            msg.attach(MIMEText(content))

            with open(file_name, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name = basename(file_name).decode('utf-8')
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file_name).decode('utf-8')
            print(part['Content-Disposition'])
            msg.attach(part)

            conn = SMTP(self.config.smtp_server)
            conn.set_debuglevel(False)
            conn.login(self.config.smtp_username, self.config.smtp_password)
            try:
                conn.sendmail(self.config.smtp_sender, destination, msg.as_string())
            finally:
                conn.quit()

            return True
        except Exception:
            import traceback
            traceback.print_exc()
            return False
