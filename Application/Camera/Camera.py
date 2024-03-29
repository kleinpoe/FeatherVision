
from datetime import datetime
from logging import Logger
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import Output

from Camera.Frames.ObjectDetectionFrame import ObjectDetectionFrame
from Camera.PreviewFrameToRgbConverter import PreviewFrameToRgbConverter
from Camera.Outputs.SynchronizationOutput import SynchronizationOutput
from Camera.Outputs.MultiOutput import MultiOutput
from Config.Config import Config

class Camera:
    def __init__(self,output: Output, frameConverter:PreviewFrameToRgbConverter, referenceTimestamp: datetime, config: Config, logger:Logger ):
        self.frameConverter = frameConverter
        self.logger = logger
        self.camera = Picamera2()
        self.config = config
        self.synchronizationOutput = SynchronizationOutput(referenceTimestamp)
        self.output = MultiOutput([output,self.synchronizationOutput])
        self.videoConfiguration = self.camera.create_video_configuration(main={"size":config.Camera.MainResolution},
                                                        lores={"size":config.Camera.ObjectDetectionResolution},
                                                        controls={'FrameRate':config.Camera.Fps})
        self.camera.configure(self.videoConfiguration)
        self.mainEncoder= H264Encoder(framerate=config.Camera.Fps)
        
    def Start(self) -> None:
        self.logger.info(f"Starting Camera. FPS={self.config.Camera.Fps} MainResolution={self.config.Camera.MainResolution}")
        self.camera.start_recording(self.mainEncoder, self.output)
        
    def Stop(self) -> None:
        self.logger.info(f"Shutting down Camera.")
        self.camera.stop_recording()
        self.camera.close()
        
    def CaptureObjectDetectionFrame(self) -> ObjectDetectionFrame:
        request = self.camera.capture_request()
        frame = request.make_array(name='lores')
        #metadata = request.get_metadata()
        request.release()
        timestamp = self.synchronizationOutput.GetCurrentTimestamp()
        rgbFrame = self.frameConverter.ConvertToRgb(frame)
        return ObjectDetectionFrame(rgbFrame, timestamp )
        #log(f'Captured New LoRes-Frame: NumberOfBytes={len(frame)}, Timestamps[{timestamp1}-{timestamp2}] TimeStamp={timestamp}µs')