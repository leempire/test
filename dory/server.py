import json
import time
from socket import *
from threading import Thread


class _Server1:
    """服务端口"""

    def __init__(self, process, host, token, password='ichat', num=10):
        """
        process: 函数，输入为msg,user
        host,token
        """
        self.host = (host, token)
        self.num = num  # 开放用户数量
        self.soc = self.start()
        self.group = _Group(password, process)  # 储存用户的容器
        self.add_user()

    def start(self):
        """启动服务器"""
        soc = socket(AF_INET, SOCK_STREAM)
        soc.bind(self.host)
        soc.listen(self.num)
        return soc

    def add_user(self):
        """添加用户端"""
        while True:
            connection, address = self.soc.accept()
            Thread(target=self.group.add_user, args=(connection, ), daemon=True).start()


class _Group:
    def __init__(self, password, process):
        self.password = password
        self.process = process
        self.group = []
        self.process.group = self.group

    def add_user(self, connection):
        user = _User(connection, self)
        token = user.get_msg()
        if type(token) != dict:
            return
        if 'type' not in token or 'data' not in token:
            return
        if token['type'] != 'password' or token['data'] != self.password:
            return
        user.start()
        self.group.append(user)
        self.process.login(user)

    def out(self, user):
        for i in range(len(self.group)):
            if self.group[i] == user:
                del self.group[i]
                break


class _User:
    def __init__(self, connection, group):
        """每分钟要发一次{'type': 'alive'}保证存活"""
        self.alive = True
        self.checking = True
        self.group = group
        self.connection = connection
        self.number = connection.fileno()

    def __eq__(self, other):
        return self.number == other.number

    def out(self):
        """退出"""
        if not self.alive:
            return
        self.group.out(self)
        self.alive = False
        self.connection.close()
        self.group.process.out(self)

    def start(self):
        """启动时初始化"""
        Thread(target=self._listen, daemon=True).start()
        Thread(target=self._check_alive, daemon=True).start()

    def _check_alive(self):
        while self.alive:
            self.checking = False
            time.sleep(90)
            if not self.checking:
                self.out()

    def _listen(self):
        """监听信息"""
        while self.alive:
            msg = self.get_msg()
            if msg:
                self.group.process.act(msg, self)

    def get_msg(self):
        """接受信息，返回解码后的信息。过程中程序静止，若期间连接断开，产生报错"""
        try:
            tmp = ''
            while '/*/' not in tmp:
                tmp += self.connection.recv(1024).decode()
            a = tmp.split('/*/')
            msg, tmp = a[0], '/*/'.join(a[1:])
            msg = json.loads(msg)
            if msg['type'] == 'alive':
                self.checking = True
                return ''
            return msg
        except Exception:
            self.out()
            return ''

    def send_msg(self, msg):
        """向该用户发送msg，传入为字符串msg"""
        try:
            msg = json.dumps(msg) + '/*/'
            self.connection.send(msg.encode())
        except Exception:
            self.out()


class Server:
    def __init__(self):
        self.group = []

    def connect(self, host, token, password='ichat', num=10):
        _Server1(self, host, token, password, num)

    def act(self, msg, user):
        """处理消息"""
        for u in self.group:
            if u != user:
                u.send_msg(msg)

    def login(self, user):
        """用户连接时触发"""
        pass

    def out(self, user):
        """用户离开时触发"""
        pass


if __name__ == '__main__':
    s = Server()
    s.connect('127.0.0.1', 50000)
