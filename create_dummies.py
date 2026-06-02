from PIL import Image
from moviepy import AudioArrayClip
import numpy as np
import os

print("Creating dummy assets...")
Image.new('RGB', (1920, 1080), color=(20, 20, 50)).save('bg_image.png')
print("Created bg_image.png")

AudioArrayClip(np.zeros((5 * 44100, 2)), fps=44100).write_audiofile('clip.mp3', fps=44100, logger=None)
print("Created clip.mp3")
