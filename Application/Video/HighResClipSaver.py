from dataclasses import dataclass
from pathlib import Path
from Camera.Outputs.CircularBufferOutput import CircularBufferOutput
from Config.Config import Config
from Video.FilePathProvider import FilePathProvider


import os
import subprocess
from datetime import datetime, timedelta
from logging import Logger


class HighResClipSaver:
    def __init__(self, highResBuffer: CircularBufferOutput, filePathProvider: FilePathProvider, config: Config, logger: Logger ):
        self.filePathProvider = filePathProvider
        self.highResBuffer = highResBuffer
        self.config = config
        self.logger = logger
        
    @dataclass
    class Result:
        FilePath:str
        Duration:timedelta
        NumberOfFrames:int

    def Save(self, timestamp: datetime, clipBegin: datetime, clipEnd: datetime ) -> Result:

        temporaryFilePath = self.filePathProvider.GetTemporaryClipPath(timestamp, 'h264')
        highResFilePath = self.filePathProvider.GetHighResClipPath(timestamp,'mp4')
        
        Path(highResFilePath).parent.mkdir(parents=True, exist_ok=True)

        fps = self.config.Camera.Fps
        richFrames = self.highResBuffer.GetFrames(clipBegin, clipEnd)
        lengthInSeconds = len(richFrames) / fps
        sizeInMb = sum([len(x.Frame) for x in richFrames]) / 1E6

        self.logger.debug(f'Writing High-Resolution Video: Frames:{len(richFrames)}, Duration:{lengthInSeconds}s, Size:{sizeInMb}MB. Temporary file: "{temporaryFilePath}", Video File: "{highResFilePath}"')

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

        return HighResClipSaver.Result(highResFilePath, timedelta(seconds=lengthInSeconds), len(richFrames))