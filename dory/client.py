import socket
import threading
import json
import time


class _User:
    def __init__(self, process, host, token, password='ichat'):
        self.process = process
        self.process.send = self.send_msg
        self.password = password
        self.host = (host, token)
        self.alive = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.start()

    def start(self):
        try:
            self.sock.connect(self.host)
            self.send_msg({'type': 'password', 'data': self.password})
            self.alive = True
            threading.Thread(target=self.listen, daemon=True).start()
            threading.Thread(target=self.keep_alive, daemon=True).start()
            self.process.login()
        except Exception:
            self.process.out()

    def out(self):
        if not self.alive:
            return
        self.alive = False
        self.sock.close()
        self.process.out()

    def keep_alive(self):
        while True:
            time.sleep(60)
            self.send_msg({'type': 'alive'})

    def listen(self):
        while self.alive:
            msg = self.get_msg()
            if msg:
                self.process.act(msg)

    def get_msg(self):
        try:
            tmp = ''
            while '/*/' not in tmp:
                tmp += self.sock.recv(1024).decode()
            a = tmp.split('/*/')
            msg, tmp = a[0], '/*/'.join(a[1:])
            msg = json.loads(msg)
            return msg
        except Exception:
            self.out()
            return ''

    def send_msg(self, msg):
        try:
            if type(msg) != dict:
                msg = {'type': 'common', 'data': msg}
            elif 'type' not in msg:
                msg = {'type': 'common', 'data': msg}
            msg = json.dumps(msg) + '/*/'
            self.sock.send(msg.encode())
        except Exception:
            self.out()


class Client:
    def __init__(self):
        pass

    def connect(self, host, token, password='ichat'):
        _User(self, host, token, password)

    def send(self, msg):
        """发送消息，此方法会被覆写"""
        pass

    def act(self, msg):
        """处理消息"""
        pass

    def login(self):
        """连接成功时触发"""
        pass

    def out(self):
        """断开连接时触发"""
        pass


if __name__ == '__main__':
    process = Client()
    process.connect('127.0.0.1', 50000)
    while True:
        process.send(input(''))
