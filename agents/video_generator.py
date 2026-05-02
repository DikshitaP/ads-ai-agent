import os
import json
import requests
from pathlib import Path
from moviepy import (
    ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip
)
from gtts import gTTS
import textwrap
import requests


class VideoGenerator:
    def __init__(self):
        self.output_dir = "output/videos"
        os.makedirs(self.output_dir, exist_ok=True)
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")  # Add to .env
    
    def get_real_image(self, visual_description, scene_num):
        """Get real stock photo from Pexels based on visual description"""
        if not self.pexels_api_key:
            return self.get_image_for_scene(visual_description, scene_num)

        # Extract keywords from visual description
        keywords = {
            "person sitting at computer": "trader computer",
            "split-screen comparison": "chart comparison",
            "mobile alerts": "phone notification",
            "crowd sentiment": "crowd analysis",
            "trading dashboard": "trading screen",
            "testimonials": "testimonial",
            "statistics": "statistics chart",
            "call-to-action": "sign up button"
        }

         # Map scene description to search query
        query = "trading"
        for key, value in keywords.items():
            if key in visual_description.lower():
                query = value
                break
        try:
            url = "https://api.pexels.com/v1/search"
            headers = {"Authorization": self.pexels_api_key}
            response = requests.get(url, headers=headers, params={"query": query, "per_page": 3})
            
            if response.status_code == 200:
                photos = response.json().get("photos", [])
                if photos:
                    photo_url = photos[0]["src"]["large2x"]
                    img_response = requests.get(photo_url)
                    image_file = f"{self.output_dir}/scene_{scene_num}_real.jpg"
                    with open(image_file, "wb") as f:
                        f.write(img_response.content)
                    print(f"  📸 Got real image from Pexels for scene {scene_num}")
                    return image_file
        except Exception as e:
            print(f"  ⚠️ Pexels failed: {e}")
        
        # Fallback to placeholder
        return self.get_image_for_scene(visual_description, scene_num)

    def load_script(self, script_file="data/script.json"):
        """Load the generated script"""
        with open(script_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def generate_voiceover_gtts(self, text, scene_num):
        """Convert text to speech using gTTS (free, no API key)"""
        try:
            audio_file = f"{self.output_dir}/scene_{scene_num}_audio.mp3"
            
            # Use gTTS with English
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(audio_file)
            
            print(f"  🎤 Generated audio for scene {scene_num} (gTTS)")
            return audio_file
            
        except Exception as e:
            print(f"  ❌ Audio generation failed: {e}")
            return None
    
    def get_image_for_scene(self, visual_description, scene_num):
        """Create better looking images with colors and icons"""
        from PIL import Image, ImageDraw, ImageFont
        
        image_file = f"{self.output_dir}/scene_{scene_num}.png"
        
        # Use different colors per scene
        colors = [
            (70, 70, 100), (100, 70, 70), (70, 100, 70),
            (100, 100, 70), (70, 100, 100), (100, 70, 100),
            (80, 80, 100), (100, 80, 80),
        ]
        
        color = colors[(scene_num - 1) % len(colors)]
        img = Image.new('RGB', (1280, 720), color=color)
        d = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 40)
            font_small = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw header
        d.rectangle([(0, 0), (1280, 80)], fill=(255, 215, 0))
        d.text((50, 25), "CROWDWISDOM TRADING", fill=(0, 0, 0), font=font)
        
        # Draw scene number
        d.text((50, 150), f"SCENE {scene_num}", fill=(255, 255, 255), font=font)
        
        # Wrap and draw visual description
        wrapped = textwrap.wrap(visual_description, width=40)
        y = 250
        for line in wrapped:
            d.text((50, y), line, fill=(255, 255, 255), font=font_small)
            y += 35
        
        # Draw a simple icon/placeholder
        d.rectangle([(800, 200), (1200, 500)], outline=(255, 255, 255), width=3)
        d.text((950, 350), "📊", fill=(255, 255, 255), font=font)
        
        img.save(image_file)
        return image_file
    
    def create_scene_video(self, scene, scene_num):
        """Create a video clip for one scene"""
        print(f"🎬 Creating scene {scene_num}: {scene['visual'][:50]}...")
        
        # Generate voiceover using gTTS
        audio_file = self.generate_voiceover_gtts(scene['voiceover'], scene_num)
        
        # Get image for this scene
        image_file = self.get_real_image(scene['visual'], scene_num)
        
        # Calculate duration based on voiceover length
        duration = 8  # Default
        
        if audio_file:
            try:
                audio_clip = AudioFileClip(audio_file)
                duration = audio_clip.duration
            except:
                pass
        
        # Create video clip from image
        image_clip = ImageClip(image_file, duration=duration)
        
        # Add audio if available
        if audio_file:
            try:
                audio_clip = AudioFileClip(audio_file)
                image_clip = image_clip.with_audio(audio_clip)
            except:
                pass
        
        return image_clip
    
    def assemble_video(self, script):
        """Combine all scenes into final video"""
        video_clips = []
        
        print(f"\n🎥 Generating {len(script['scenes'])} scenes...")
        
        for i, scene in enumerate(script['scenes'], 1):
            clip = self.create_scene_video(scene, i)
            video_clips.append(clip)
        
        # Concatenate all clips
        print("\n✂️  Concatenating scenes...")
        final_video = concatenate_videoclips(video_clips, method="compose")
        
        # Output file
        output_file = f"{self.output_dir}/final_ad_60s_with_audio.mp4"
        final_video.write_videofile(output_file, fps=24, codec='libx264', audio_codec='aac')
        
        print(f"\n✅ Video saved to: {output_file}")
        return output_file


if __name__ == "__main__":
    generator = VideoGenerator()
    script = generator.load_script("data/script.json")
    
    print("📖 Script loaded. Starting video generation...")
    print("⏱️  This may take 2-5 minutes...")
    
    video_file = generator.assemble_video(script)
    
    print(f"\n🎬 Complete! Watch your ad: {video_file}")