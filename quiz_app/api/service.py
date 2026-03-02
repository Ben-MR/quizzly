import json
import os
import re
from time import time
import uuid
import yt_dlp
from django.conf import settings
from google import genai
from .prompt import QUIZ_GEN_PROMPT
import google.generativeai as genai



def download_youtube_audio(video_url: str) -> str:
    """
    Downloads the audio track from a YouTube video and saves it as an M4A file.
    Uses yt-dlp with FFmpeg post-processing for high-quality audio extraction.
    
    Args:
        video_url (str): The full URL of the YouTube video.
    Returns:
        str: The relative path to the saved audio file within the media directory.
    """
    filename = f"{uuid.uuid4()}.m4a"
    output_path = os.path.join(settings.MEDIA_ROOT, "audio", filename)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    ydl_opts = {
        "format": "m4a/bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
        }],
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    return os.path.join("audio", filename)

    
def generate_quiz_from_audio(file_path):
    """
    Uploads an audio file to Google Gemini AI, waits for processing, 
    and generates a structured quiz JSON based on a predefined prompt.
    Automatically cleans up local and cloud files after processing.
    
    Args:
        file_path (str): The local absolute path to the audio file.
    Returns:
        dict: The parsed quiz data or an error dictionary.
    """
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-flash-latest')
    
    try:
        file = genai.upload_file(path=file_path)
        
        while file.state.name == "PROCESSING":
            time.sleep(2)
            file = genai.get_file(file.name)
            
        response = model.generate_content([QUIZ_GEN_PROMPT, file])
        file.delete()
        if os.path.exists(file_path):
            os.remove(file_path)

        data = re.search(r'\{.*\}', response.text, re.DOTALL).group()
        return json.loads(data)

    except Exception as e:
        return {"error": str(e)}