import io
from fastapi import UploadFile
from pypdf import PdfReader
from youtube_transcript_api import YouTubeTranscriptApi
import re

async def process_pdf(file: UploadFile) -> str:
    content = await file.read()
    reader = PdfReader(io.BytesIO(content))
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    if not text.strip():
        raise ValueError("Could not extract any text from the PDF.")
    return text

def process_youtube(url: str) -> str:
    # Extract video ID from various YouTube URL formats
    video_id_match = re.search(r'(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})', url)
    if not video_id_match:
        raise ValueError("Invalid YouTube URL. Could not extract video ID.")
    
    video_id = video_id_match.group(1)
    
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id)
    
    text = " ".join([snippet.text for snippet in transcript.snippets])
    
    if not text.strip():
        raise ValueError("Transcript was empty for this video.")
    
    return text
