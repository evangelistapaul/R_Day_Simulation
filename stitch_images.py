# -*- coding: utf-8 -*-
"""
Created on Thu Oct 30 14:11:22 2025

@author: paul.evangelista
"""

import cv2
import os
import re

from config import (
    dir_setup
)

image_folder_path = dir_setup()
os.chdir(image_folder_path)

def pngs_to_video_opencv(image_folder, output_video_path, fps=30):
    """Stitches PNGs from a folder into a video using OpenCV."""
    
    # 1. Get and sort image files
    images = [img for img in os.listdir(image_folder) if img.endswith("Rday.png")]
    # Crucial: Sort numerically to ensure correct frame order
    images.sort(key=lambda f: int(''.join(filter(str.isdigit, f)) or 0)) 
    
    if not images:
        print("No PNG images found in the folder.")
        return

    # 2. Read the first image to get dimensions
    first_image_path = os.path.join(image_folder, images[0])
    frame = cv2.imread(first_image_path)
    height, width, layers = frame.shape
    size = (width, height)

    # 3. Define the codec and create VideoWriter object
    # 'mp4v' for MP4 on most systems. Use 'DIVX' for AVI.
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    video = cv2.VideoWriter(output_video_path, fourcc, fps, size)

    # 4. Iterate and write frames
    print(f"Starting video creation with {len(images)} frames...")
    for image_file in images:
        img_path = os.path.join(image_folder, image_file)
        frame = cv2.imread(img_path)
        # Ensure image loads correctly before writing
        if frame is not None:
             video.write(frame)
        else:
             print(f"Warning: Could not read image {image_file}. Skipping.")
    
    # 5. Release the video writer
    video.release()
    print(f"Video saved successfully to {output_video_path}")

dir_list = os.listdir('.')
Rday_png_list = [
    s for s in dir_list 
    if re.search('.*Rday.png$', s)
]

fps_rate = len(Rday_png_list)/30 #always a 30-second video

with open("recent_run.txt", "r") as file:
    path_descr = file.read()
    
output_file = 'stitched_video_' + path_descr.replace(" ","_") + ".mp4"
pngs_to_video_opencv(image_folder_path, output_file, fps=fps_rate)
