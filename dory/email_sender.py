import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


class EmailSender:
    """南灵邮递员"""

    def __init__(self, user='809308568@qq.com', code='rznxiphyfadvbbjh', server=('smtp.qq.com', 465)):
        """初始化"""
        # 用户和密码
        self.user = user
        self.code = code
        # 初始化
        self.title, self.text, self.file = None, None, None
        self.smtp = smtplib.SMTP_SSL(*server)
        self.smtp.login(self.user, self.code)

    def set_message(self, title=None, text=None, file=None):
        """设置信息"""
        self.title = title or self.title
        self.text = text or self.text
        self.file = file or self.file

    def send_message(self, receiver, quit_=True):
        """发送邮件"""
        # 加载头部信息
        message = self._set_head(receiver)
        # 添加附件
        self._attach_file(message)
        # 载入正文
        self._set_text(message)
        # 发送
        self.smtp.sendmail(self.user, receiver, str(message))
        # 退出
        if quit_:
            self.quit()

    def _set_head(self, receiver):
        message = MIMEMultipart()
        message['subject'] = self.title  # 标题
        message['from'] = self.user  # 发送者
        if type(receiver) == str:
            message['to'] = receiver
        else:
            message['to'] = ';'.join(receiver)  # 接收者
        return message

    def _attach_file(self, message):
        if self.file:
            part = MIMEApplication(open(self.file, 'rb').read())
            part.add_header('Content-Disposition', 'attachment', filename=self.file)
            message.attach(part)

    def _set_text(self, message):
        text = MIMEText(self.text)
        message.attach(text)

    def quit(self):
        """退出"""
        self.smtp.quit()


if __name__ == '__main__':
    sender = EmailSender('3356884983@qq.com', 'ojcicelwppltchcf')
    sender.set_message('test_title', 'test')
    sender.send_message(['李多锐'])
