from Camera.PreviewFrameToRgbConverter import PreviewFrameToRgbConverter
from Camera.Outputs.MultiOutput import MultiOutput
from Camera.Outputs.CircularBufferOutput import CircularBufferOutput
from Camera.Outputs.StreamOutput import StreamOutput
from Infrastructure.Clock import Clock
from Camera.Camera import Camera
from WebInterface.StreamingHandlerManager import StreamingHandlerManager
from WebInterface.WebServer import WebServer
from Config.RuntimeConfig import RuntimeConfig
from Config.Config import Config
from Infrastructure.LoggerFactory import LoggerFactory
from Infrastructure.NetworkChecker import NetworkChecker
from Infrastructure.PerformanceMonitor import PerformanceMonitor

# infrastructure
runtimeConfig = RuntimeConfig()
config = Config(runtimeConfig)
loggerFactory = LoggerFactory(config)
logger = loggerFactory.CreateLogger()
networkChecker = NetworkChecker(logger)
performanceMonitor = PerformanceMonitor(config, networkChecker, logger)
clock = Clock()

# web interface
streamingHandlerManager = StreamingHandlerManager(config, logger)
webServer = WebServer(streamingHandlerManager, config, logger)

def getBroadcastFunc(loop:tornado.ioloop.IOLoop):
    def broadcastFunc(richFrame:RichFrame):
        if loop is not None and wsHandler.hasConnections():
            loop.add_callback(callback=wsHandler.broadcast, frame=richFrame.Frame, timestamp=richFrame.Timestamp, isKeyframe=richFrame.IsKeyframe)
    return broadcastFunc

# camera
referenceTimestamp = clock.Now()
circularBufferOutput = CircularBufferOutput(referenceTimestamp, config)
streamOutput = StreamOutput(referenceTimestamp, streamingHandlerManager.Broadcast)
output = MultiOutput([streamOutput,circularBufferOutput])
frameConverter = PreviewFrameToRgbConverter(config)
camera = Camera(output,frameConverter,referenceTimestamp,config,logger)

try:
    camera.Start()
    webServer.Start()
except KeyboardInterrupt:
    logger.info("Exiting Application due to Keyboard Interrupt.")
finally:
    logger.info("Shutting down threads.")
    camera.Stop()
    webServer.Stop()
    logger.info("Shutdown successful, exiting application.")