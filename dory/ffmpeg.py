import os


class FFMPEG:
    def __init__(self, ffmpegPath="E:/Python/dory/tool/ffmpeg.exe"):
        self.ffmpegPath = self.getAbsName(ffmpegPath)

    @staticmethod
    def getAbsName(path):
        return os.path.abspath(path)

    def transformFormat(self, filename, newname):
        if type(newname) == list:
            tmp = ''
            for n in newname:
                tmp += '"{}" '.format(self.getAbsName(n))
            newname = tmp
        else:
            newname = '"{}"'.format(self.getAbsName(newname))
        order = '"{}" -i "{}" {}'.format(self.ffmpegPath, self.getAbsName(filename), newname)
        os.system(order)

    def getAudio(self, mp4Name, audioName):
        order = '{} -i "{}" -vn "{}"'.format(self.ffmpegPath, self.getAbsName(mp4Name), self.getAbsName(audioName))
        os.system(order)

    def compressVideo(self, mp4Name):
        order = '{} -i "{}" -c:v libx264 -ac 2 -c:a aac -strict -2 -b:a 128k -crf 28 video_output.mp4'\
            .format(self.ffmpegPath, mp4Name)
        os.system(order)


if __name__ == '__main__':
    tool = FFMPEG()
    tool.compressVideo('作业1.mp4')
