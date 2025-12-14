import requests
from PIL import Image
from io import BytesIO
import streamlit as st

def upload_to_tmpfiles(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    buffered.seek(0)
    
    files = {'file': ('ref.png', buffered, 'image/png')}
    try:
        response = requests.post("https://tmpfiles.org/api/v1/upload", files=files, timeout=30)
        if response.status_code == 200:
            data = response.json()["data"]
            return data["url"].replace("/dl/", "/")
    except:
        pass
    return None

def upload_references(face_files=None, pose_file=None, bg_file=None):
    refs = {"face_urls": [], "pose_url": None, "bg_url": None}
    
    if face_files:
        for file in face_files:
            img = Image.open(file)
            url = upload_to_tmpfiles(img)
            if url:
                refs["face_urls"].append(url)
    
    if pose_file:
        img = Image.open(pose_file)
        url = upload_to_tmpfiles(img)
        if url:
            refs["pose_url"] = url
    
    if bg_file:
        img = Image.open(bg_file)
        url = upload_to_tmpfiles(img)
        if url:
            refs["bg_url"] = url
    
    return refs

def enhance_nsfw_prompt(prompt: str) -> str:
    boosters = [", highly detailed anatomy", ", sharp focus, 8k", ", cinematic lighting", ", explicit, no censorship", ", masterpiece, best quality"]
    return prompt + " " + " ".join(boosters)

def get_venice_link(prompt: str, reference_url: str = None):
    base = "https://venice.ai/image-generation"
    params = f"?prompt={prompt.replace(' ', '%20')}"
    if reference_url:
        params += f"&reference={reference_url}"
    return base + params

def get_perchance_link(prompt: str, reference_url: str = None):
    base = "https://perchance.org/ai-text-to-image-generator"
    params = f"?prompt={prompt.replace(' ', '%20')}"
    if reference_url:
        params += f"&referenceImage={reference_url}"
    return base + params

def get_perchance_video_link(image_url: str, motion_prompt: str = "smooth erotic motion"):
    return f"https://perchance.org/ai-text-to-video-generator?image={image_url}&prompt={motion_prompt.replace(' ', '%20')}"
