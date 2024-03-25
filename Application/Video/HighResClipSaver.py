from Application.Camera.Outputs.CircularBufferOutput import CircularBufferOutput
from Application.Config.Config import Config
from Application.Video.Saving.FilePathProvider import FilePathProvider


import os
import subprocess
from datetime import datetime
from logging import Logger


class HighResClipSaver:
    def __init__(self, filePathProvider: FilePathProvider, config: Config, logger: Logger ):
        self.filePathProvider = filePathProvider
        self.config = config
        self.logger = logger

    def Save(self, timestamp: datetime, buffer: CircularBufferOutput, clipBegin: datetime, clipEnd: datetime ):

        temporaryFilePath = self.filePathProvider.GetTemporaryClipPath(timestamp, 'h264')
        highResFilePath = self.filePathProvider.GetHighResClipPath(timestamp,'mp4')

        fps = self.config.Camera.Fps
        richFrames = buffer.GetFrames(clipBegin, clipEnd)
        lengthInSeconds = len(richFrames) / fps
        sizeInMb = sum([len(x.Frame) for x in richFrames]) / 1E6

        self.logger.info(f'Writing High-Resolution Video: Frames:{len(richFrames)}, Duration:{lengthInSeconds}s, Size:{sizeInMb}MB. Temporary file: "{temporaryFilePath}", Video File: "{highResFilePath}"')

        # Write Circular Buffer to h264 file
        with open(temporaryFilePath, "wb") as file:
            for richFrame in richFrames:
                file.write(richFrame.Frame)

        # Convert h264 file to mp4
        command = ["ffmpeg", "-loglevel", "error", "-r", str(fps), "-i", temporaryFilePath, "-movflags", "+faststart", "-y", "-c", "copy", highResFilePath]
        returnCode = subprocess.call(command)
        if returnCode is not 0:
            self.logger.error(f'Error during conversion of "{temporaryFilePath}" to "{highResFilePath}"')
            raise RuntimeError("Error during conversion of high res video file.")

        # Delete temporary file
        os.remove(temporaryFilePath)

        return highResFilePath