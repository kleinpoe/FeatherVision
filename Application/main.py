from Surveillance.DetectionBroadcaster import DetectionBroadcaster
from Surveillance.History.DetectionHistory import DetectionHistory
from Surveillance.ObjectDetection.ImagePreparation import ImagePreparation
from Surveillance.ObjectDetection.ObjectDetection import ObjectDetector
from Video.AnnotatedClipSaver import AnnotatedClipSaver
from Video.ClipSaver import ClipSaver
from Video.FilePathProvider import FilePathProvider
from Video.FrameAnnotator import FrameAnnotator
from Video.HighResClipSaver import HighResClipSaver
from Video.ThumbnailSaver import ThumbnailSaver
from Surveillance.FrameAnalyzer import FrameAnalyzer
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

# camera
referenceTimestamp = clock.Now()
circularBufferOutput = CircularBufferOutput(referenceTimestamp, config)
streamOutput = StreamOutput(referenceTimestamp, webServer.GetCallback(streamingHandlerManager.Broadcast))
output = MultiOutput([streamOutput,circularBufferOutput])
frameConverter = PreviewFrameToRgbConverter(config)
camera = Camera(output,frameConverter,referenceTimestamp,config,logger)

# object detection
imagePreparation = ImagePreparation()
detector = ObjectDetector(imagePreparation,config)
detectionBroadcaster = DetectionBroadcaster(webServer.GetCallback(streamingHandlerManager.UpdateDetections), config)
detectionHistory = DetectionHistory(config,logger)
filePathProvider = FilePathProvider(config)
highResClipSaver = HighResClipSaver(circularBufferOutput,filePathProvider,config,logger)
frameAnnotator = FrameAnnotator(config)
annotatedClipSaver = AnnotatedClipSaver(filePathProvider,frameAnnotator,logger,config)
thumbnailSaver = ThumbnailSaver(filePathProvider, config, logger)
clipSaver = ClipSaver(highResClipSaver,annotatedClipSaver,thumbnailSaver,clock,logger,config)
frameAnalyzer = FrameAnalyzer(detector,camera, detectionBroadcaster,detectionHistory,clipSaver,config,logger)

try:
    camera.Start()
    frameAnalyzer.Start()
    webServer.Start()
except KeyboardInterrupt:
    logger.info("Exiting Application due to Keyboard Interrupt.")
finally:
    logger.info("Shutting down threads.")
    frameAnalyzer.Stop()
    camera.Stop()
    webServer.Stop()
    logger.info("Shutdown successful, exiting application.")