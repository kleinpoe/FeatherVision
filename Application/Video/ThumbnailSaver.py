from Application.Config.Config import Config
from Application.Video.Saving.FilePathProvider import FilePathProvider


import subprocess
from datetime import datetime
from logging import Logger


class ThumbnailSaver:
    def __init__(self, filePathProvider: FilePathProvider, numberOfFramesOfHighResVideoFile:int, config: Config, logger: Logger):
        self.filePathProvider = filePathProvider
        self.numberOfFramesOfHighResVideoFile = numberOfFramesOfHighResVideoFile
        self.config = config
        self.logger = logger

    def Save(self, timestamp: datetime, highResVideoFilePath: str):
        # ffmpeg -ss 2 -i "20220220-145106_Birdbuddy.mp4" -frames 4 -vf "select=not(mod(n\,30)),scale=320:180,tile=2x2" -vsync vfr -q:v 10 20220220-145106_Birdbuddy.jpg
        filePath = self.filePathProvider.GetHighResClipPath(timestamp, 'jpg')
        secondsPaddingStart = self.config.ClipGeneration.PaddingStart.total_seconds()
        frames = self.numberOfFramesOfHighResVideoFile
        self.logger.info(f'Creating Thumbnail at "{filePath}" for video "{highResVideoFilePath}"')
        command = ['ffmpeg', '-loglevel', 'error', '-ss', str(secondsPaddingStart), '-i', highResVideoFilePath, '-frames:v', '1', '-vf', f'select=not(mod(n\,{frames})),scale=320:180,tile=2x2', '-vsync', 'vfr', '-q:v', '10', filePath]
        returnCode = subprocess.call(command)
        if returnCode is not 0:
            self.logger.error(f'Error during generation of thumbnail "{filePath}" for video "{highResVideoFilePath}".')
            raise RuntimeError("Error during generation of thumbnail.")
        return filePath