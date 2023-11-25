import os
import shutil
import json
import hashlib


def file_to_md5(filename):
    with open(filename, 'rb') as f:
        md5 = hashlib.md5(f.read()).hexdigest()
    return md5


class Json:
    register = {}

    class MyJsonEncoder(json.JSONEncoder):
        def default(self, obj):
            for c in Json.register.values():
                if isinstance(obj, c):
                    return obj.to_dict()
            else:
                return json.JSONEncoder.default(self, obj)

    class MyJsonDecoder(json.JSONDecoder):

        def __init__(self, *args, **kwargs):
            super().__init__(object_hook=self.object_hook, *args, **kwargs)

        def object_hook(self, o):
            if o.get('__class__') in Json.register:
                return Json.register[o.get('__class__')].from_dict(o)
            return o

    @staticmethod
    def json_load(filename, encoding='utf-8'):
        with open(str(filename), encoding=encoding) as f:
            return json.load(f, cls=Json.MyJsonDecoder)

    @staticmethod
    def json_dump(obj, filename, encoding='utf-8'):
        with open(str(filename), 'w', encoding=encoding) as f:
            json.dump(obj, f, indent=2, ensure_ascii=False, cls=Json.MyJsonEncoder)

    @staticmethod
    def json_dumps(obj):
        return json.dumps(obj, cls=Json.MyJsonEncoder)

    @staticmethod
    def json_loads(obj):
        return json.loads(obj, cls=Json.MyJsonDecoder)


class Path:
    def __init__(self, path=''):
        if isinstance(path, Path):
            self.path = path.path
        else:
            self.path = os.path.abspath(path)

    @property
    def type(self):
        if os.path.isdir(self.path):
            return 'dir'
        return os.path.splitext(self.path)[1]

    @property
    def name(self):
        basename = self.basename
        return basename[:basename.rfind('.')]

    @property
    def dirname(self):
        return os.path.dirname(self.path)

    @property
    def basename(self):
        return os.path.basename(self.path)

    @property
    def exists(self):
        return os.path.exists(self.path)

    @property
    def size(self):
        return os.path.getsize(self.path)

    @property
    def md5(self):
        return file_to_md5(self.path)

    def write(self, content, encoding='utf-8'):
        if not self.type:
            raise TypeError
        Path('').create_dir(self.dirname)
        if self.type == '.json':
            Json.json_dump(content, self.path, encoding=encoding)
        else:
            with open(self.path, 'w', encoding=encoding) as f:
                f.write(content)

    def read(self, encoding='utf-8'):
        if not self.type:
            raise TypeError
        if self.type == '.json':
            return Json.json_load(self.path, encoding=encoding)
        else:
            with open(self.path, encoding=encoding) as f:
                return f.read()

    def move(self, new_path):
        """移动到新地址"""
        new_path = Path(new_path)
        self.create_dir(new_path)
        shutil.move(self.path, new_path.path)

    def remove(self):
        """删除文件或目录"""
        if os.path.isdir(self.path):
            shutil.rmtree(self.path)
        else:
            os.remove(self.path)

    def rename(self, name):
        os.rename(self.path, str(self.get_parent() / name))

    def get_parent(self):
        """获取父目录"""
        return Path(self.dirname)

    def list_dir(self):
        """获取所有子目录及文件"""
        if os.path.isdir(self.path):
            return [Path((self / i).path) for i in os.listdir(self.path)]
        else:
            return []

    def create_dir(self, name=None):
        """创建目录"""
        if name is None:
            self.create_dir(self)
            return
        if type(name) == list:
            result = []
            for i in name:
                result.append(self.create_dir(i))
            return result
        if not isinstance(name, Path):
            name = Path(self / name)
        root = str(name).replace('\\', '/')
        dirs = root.split('/')
        root = ''
        for d in dirs:
            root += d + '/'
            if not os.path.exists(root):
                os.mkdir(root)
        return name

    def __rtruediv__(self, other):
        return Path(other) / self

    def __truediv__(self, other):
        if isinstance(other, Path):
            other = other.path
        result = os.path.join(self.path, other)
        return Path(result)

    def __str__(self):
        return self.path

    def __repr__(self):
        return str(self)

    # Json化方法
    def to_dict(self):
        return {'__class__': 'Path', 'value': self.path}

    @staticmethod
    def from_dict(obj):
        return Path(obj['value'])


Json.register['Path'] = Path
if __name__ == '__main__':
    a = Json().json_dumps(Path('./'))
    print(Json().json_loads(a))
