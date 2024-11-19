import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass
from typing import Dict, Any
from moviepy.editor import VideoFileClip, AudioFileClip
import os

@dataclass
class VideoConfig:
    fps: int = 30

class Watermark:
    def __init__(self):
        try:
            self.font = ImageFont.truetype("Rowdies-Regular.ttf", 60)
            self.font_large = ImageFont.truetype("Rowdies-Regular.ttf", 100)
        except:
            # Fallback to default font if Rowdies isn't available
            self.font = ImageFont.load_default()
            self.font_large = ImageFont.load_default()
    
    def spring(self, frame: int, stiffness: float = 100) -> float:
        omega = np.sqrt(stiffness)
        t = frame / VideoConfig.fps
        value = 1 - np.exp(-omega * t) * np.cos(omega * t)
        return min(1, max(0, value))
    
    def interpolate(self, value: float, input_range: list, output_range: list) -> float:
        input_min, input_max = input_range
        output_min, output_max = output_range
        return output_min + (value - input_min) * (output_max - output_min) / (input_max - input_min)
    
    def add_watermark(self, frame: np.ndarray, frame_number: int) -> np.ndarray:
        # Convert frame to PIL Image
        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        # Create transparent overlay
        overlay = Image.new('RGBA', frame_pil.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Calculate animation
        spring_value = self.spring(frame_number)
        y_position = int(self.interpolate(spring_value, [0, 1], [-300, 0]))
        
        # Draw text
        base_y = 100 + y_position
        draw.text((100, base_y), "AI shorts with", 
                 font=self.font, fill=(255, 255, 255, 204))  # 204 is 0.8 opacity
        draw.text((100, base_y + 70), "studiolabs.ai", 
                 font=self.font_large, fill=(255, 255, 255, 204))
        
        # Composite the frame and overlay
        frame_pil.paste(overlay, (0, 0), overlay)
        
        # Convert back to OpenCV format
        return cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)

    def process_video(self, input_path: str, output_path: str):
        # Open video
        cap = cv2.VideoCapture(input_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_number = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Apply watermark
            watermarked_frame = self.add_watermark(frame, frame_number)
            
            # Write frame
            out.write(watermarked_frame)
            frame_number += 1
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Optional: Show progress
            if frame_number % 30 == 0:
                progress = (frame_number / total_frames) * 100
                print(f"Processed frame {frame_number}/{total_frames} ({progress:.1f}%)")    
        # Cleanup
        cap.release()
        out.release()

        # Add audio back to the processed video
        temp_output = output_path
        final_output = output_path.replace('.mp4', '_with_audio.mp4')
        
        video = VideoFileClip(temp_output)
        original = VideoFileClip(input_path)
        
        final_video = video.set_audio(original.audio)
        final_video.write_videofile(final_output, codec='libx264')
        
        # Cleanup
        video.close()
        original.close()

    def process_videos_from_folder(self, input_folder: str, output_folder: str) -> None:
        """Process all videos in a folder"""
        try:
            print(f"Processing videos in {input_folder}")
            # Create output folder if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)
            
            # Get list of video files
            video_files = [f for f in os.listdir(input_folder) if f.endswith('.mp4')]
            
            if not video_files:
                print("No video files found in the input folder")
                return
            
            print(f"Found {len(video_files)} videos to process")
            
            # Process each video
            for index, file in enumerate(video_files, start=1):
                input_path = os.path.join(input_folder, file)
                output_path = os.path.join(output_folder, f"watermarked_{file}")
                
                print(f"Processing video {index}/{len(video_files)}: {file}")
                self.process_video(input_path, output_path)
                
            print("All videos processed successfully!")
            
        except Exception as e:
            print(f"Error processing folder: {e}")

