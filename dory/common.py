# coding:utf-8
import json
import os
import shutil
import win32com.client as client
import time
import threading


class Average:
    def __init__(self, gamma=1.0):
        self.avg = 0
        self.gamma = gamma
        self.tmp = 1

    def reset(self):
        self.avg = 0
        self.tmp = 1

    def add(self, data):
        self.avg = (self.tmp * self.avg + data - self.avg) / self.tmp
        self.tmp = self.tmp * self.gamma + 1
        return self.avg


def mklink2(name, target):
    from win32com.shell import shell
    from win32com.shell import shellcon
    import pythoncom
    iconname = ""
    # 设置快捷方式的起始位置，此处设置为windows启动目录
    now = os.getcwd() + '\\'
    desk = os.path.expanduser('~') + '\\Desktop\\'
    name = desk + name
    target = now + target

    shortcut = pythoncom.CoCreateInstance(
        shell.CLSID_ShellLink, None,
        pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
    shortcut.SetPath(target)
    # 设置快捷方式的起始位置, 不然会出现找不到辅助文件的情况
    shortcut.SetWorkingDirectory(os.getcwd())
    # 可有可无，没有就默认使用文件本身的图标
    shortcut.SetIconLocation(iconname, 0)
    shortcut.QueryInterface(pythoncom.IID_IPersistFile).Save(name, 0)


def mklink(name, target, icon='E:\Python\dory\icon.ico'):
    """name:快捷方式名；target:目标文件名；icon:图标地址"""
    desk = os.path.expanduser('~') + '\\Desktop\\'
    root = os.getcwd() + '\\'
    path = desk + name
    target = root + target

    shell = client.Dispatch('Wscript.Shell')
    link = shell.CreateShortCut(path)
    link.TargetPath = target
    link.IconLocation = icon
    link.save()


def install(filename, exename='', window=False, icon=r'E:\Python\dory\tool\icon.ico'):
    """将filename（不加.py）打包"""
    rootname = os.path.splitext(filename)[0]
    if not exename:
        exename = os.path.splitext(filename)[0]
    else:
        exename = os.path.splitext(exename)[0]
    window = '' if window else ' -w'
    icon = f' -i {icon}'
    os.system(f'pyinstaller -F{window}{icon} {filename} -p D:')
    shutil.move(f'dist/{rootname}.exe', f'{exename}.exe')
    shutil.rmtree('dist')
    shutil.rmtree('build')
    for f in os.listdir():
        if f.split('.')[-1] == 'spec':
            os.remove(f)
    print('成功！')


class File:
    def __init__(self, dirname='./', filename='file.json'):
        self.filename = filename
        self.dirname = dirname
        self.data = self.load()

    @property
    def filepath(self):
        return os.path.join(self.dirname, self.filename)

    def load(self):
        if not os.path.exists(self.dirname):
            os.mkdir(self.dirname)
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write('')
            data = {}
        else:
            with open(self.filepath, encoding='utf-8') as f:
                data = f.read()
                if not data:
                    data = {}
                else:
                    data = json.loads(data)
                    data = json.loads(data)
        return data

    def save(self):
        data = json.dumps(self.data, ensure_ascii=False)
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f)

    def __contains__(self, item):
        return item in self.data

    def __str__(self):
        files = '/ '.join(self.data)
        return files

    def __getitem__(self, item):
        if item in self.data:
            return self.data[item]
        else:
            return None

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]


class Timer:
    def __init__(self):
        self.t = time.time()
        self.records = []
        self.flag = True

    def record(self):
        self.records.append(time.time())

    def back(self, t):
        self.t -= t

    def tick(self):
        t = time.time()
        delta_t = t - self.t or 0.000001
        self.t = t
        return delta_t

    def thread(self, function, fps):
        def thread(_self):
            while _self.flag:
                function()
                time.sleep(1 / fps)

        self.flag = True
        threading.Thread(target=thread, daemon=True, args=(self,)).start()

    def end_thread(self):
        self.flag = False


class Progress:
    def __init__(self, total=1, mark=('■', '□'), length=20, gamma=0.95, fps=10):
        self.now, self.last, self.delta_t = 0, 0, 0
        self.total = total
        self.mark = mark
        self.length = length
        self.fps = fps
        self.key = None

        self.avg = Average(gamma)
        self.timer = Timer()

    @property
    def _prop(self):
        return self.now / self.total

    def set_total(self, total):
        self.total = total or 1

    def reset(self):
        self.now, self.last, self.delta_t = 0, 0, 0
        self.avg.reset()

    def start(self):
        self.reset()
        self.timer.thread(self.tick, self.fps)

    def end(self):
        self.timer.end_thread()
        self.tick(self.total)
        print('')

    def set_key(self, key):
        self.key = key

    def record(self, now, delta=False):
        if delta:
            now = self.now + now
        self.now = min(now, self.total)

    def tick(self, now=None, delta=False):
        if now:
            self.record(now, delta)
        elif self.key:
            self.now = self.key()
        self.delta_t = self.timer.tick()
        text = self._format_progress_bar()
        text += self._format_last_time()
        print(text, end='')
        self.last = self.now
        return self.delta_t

    def _predict_last_time(self):
        if not (self.now - self.last):
            self.timer.back(self.delta_t)
            v = self.avg.avg
        else:
            v = self.delta_t / (self.now - self.last)
            v = self.avg.add(v) or 0.0001
        remain = self.total - self.now
        return remain * v

    def _format_progress_bar(self):
        n = int(self._prop * self.length)
        bar = (self.mark[0] * n).ljust(self.length, self.mark[1])
        text = '\r进度: {} {:>5.1f}% '.format(bar, self._prop * 100)
        return text

    def _format_last_time(self):
        last_time = self._predict_last_time()
        if last_time < 1000:
            last_time = int(last_time)
        else:
            last_time = '>999'
        return '剩余时间: {:>4}s '.format(last_time)


def transform_encoding(string, target='utf-8'):
    string = string.encode(target, errors='replace')
    return string.decode(target)


def multi_task(num, function, args=()):
    ts = []
    for i in range(num):
        if args:
            t = threading.Thread(target=function, daemon=True, args=(args[i],))
        else:
            t = threading.Thread(target=function, daemon=True)
        t.start()
        ts.append(t)
    for t in ts:
        t.join()


def test_time(fun):
    def wrapped(*args, **kwargs):
        t = time.time()
        fun(*args, **kwargs)
        print('程序用时: {}s'.format(time.time() - t))
    return wrapped


if __name__ == '__main__':
    def cal(x):
        if x < 10:
            return 1
        else:
            return 2


    a = Average(0.3)
    for i in range(20):
        print(a.add(cal(i)))
