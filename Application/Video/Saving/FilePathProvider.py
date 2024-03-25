from Application.Config.Config import Config


import os
from datetime import datetime


class FilePathProvider:
    def __init__(self, config: Config):
        self.config = config

    def getDirectory(self, timestamp:datetime):
        clipDirectory = self.config.Storage.ClipsDirectory
        yearDirectoryName = str(timestamp.year)
        monthDirectoryName = str(timestamp.month)
        dayDirectoryName = str(timestamp.day)
        return os.path.join(clipDirectory, yearDirectoryName, monthDirectoryName, dayDirectoryName)

    def getFileName(self,timestamp:datetime, suffix:str, extension:str):
        formattedTimestamp = timestamp.strftime('%Y-%m-%d_%H-%M-%S')
        return f'Clip_{formattedTimestamp}_{suffix}.{extension}'

    def getFilePath(self, timestamp:datetime, suffix:str, extension:str ):
        directory = self.getDirectory(timestamp)
        fileName = self.getFileName(timestamp, suffix, extension)
        return os.path.join(directory, fileName)

    def GetThumbnailFilePath(self, timestamp:datetime, extension:str)->str:
        return self.getFilePath(timestamp, 'Thumbnail', extension)

    def GetTemporaryClipPath(self, timestamp:datetime, extension:str)->str:
        return self.getFilePath(timestamp, 'Temporary', extension)

    def GetHighResClipPath(self, timestamp:datetime, extension:str)->str:
        return self.getFilePath(timestamp, 'HighResolution', extension)

    def GetAnnotatedClipPath(self, timestamp:datetime, extension:str)->str:
        return self.getFilePath(timestamp, 'Annotated', extension)