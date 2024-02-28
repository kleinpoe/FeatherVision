#!/usr/bin/python3

from picamera2 import Picamera2
import os

picam2 = Picamera2()

root = os.path.dirname(os.path.realpath(__file__))
imagePath = os.path.join(root, "output", "test.jpg")
picam2.start()
print(f'Capturing image and saving to {imagePath}')
metadata = picam2.capture_file(imagePath)
picam2.close()