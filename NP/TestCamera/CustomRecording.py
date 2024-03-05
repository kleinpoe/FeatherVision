from datetime import timedelta
import time
import os

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput

from CustomOutput import CustomOutput

import subprocess

# setup
root = os.path.dirname(os.path.realpath(__file__))
outputDirectory = os.path.join(root,"output")
videoPath = os.path.join(outputDirectory, "test.h264")
convertedPath = os.path.join(outputDirectory, "test.mp4")

# setup camera
picam2 = Picamera2()
fps = 30
recordingDuration = timedelta(seconds=10)
videoConfig = picam2.create_video_configuration(main={"size":(1920,1080)},
                                            controls={'FrameRate':fps})
picam2.configure(videoConfig)
encoder = H264Encoder(framerate=fps)
output = CustomOutput()

# record
picam2.start_recording(encoder, output)
time.sleep(recordingDuration.total_seconds())
picam2.stop_recording()
output.stop()

# Write Circular Buffer to h264 file
with open(videoPath, "wb") as file:
    print(f"Writing frames to {videoPath}")
    size = 0
    length = output.Buffer[len(output.Buffer)-1][1]
    for frame in output.Buffer:
        file.write(frame[0])
        size = size + len(frame[0])
    print(f"Done. Length = {size/1E6}Mb. {length/1E6}s")

# Convert h264 file to mp4
print("Converting file to mp4")
command = f"ffmpeg -r {fps} -i {videoPath} -y -c copy {convertedPath}"
subprocess.call(command.split(" "))