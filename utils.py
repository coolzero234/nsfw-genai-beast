import requests
import base64
from io import BytesIO
from PIL import Image
import streamlit as st

# --- Temporary Image Upload Gratis (No Login Needed) ---
def upload_to_tmpfiles(image: Image.Image) -> str:
    """Upload image ke tmpfiles.org (gratis, no API key, uncensored, temporary ~1-7 hari)"""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    buffered.seek(0)
    
    files = {'file': ('reference.png', buffered, 'image/png')}
    response = requests.post("https://tmpfiles.org/api/v1/upload", files=files)
    if response.status_code == 200:
        json_res = response.json()
        url = json_res["data"]["url"]
        # Convert ke direct link
        direct_url = url.replace("/dl/", "/")
        return direct_url
    return None

def upload_to_imgbb(image: Image.Image, api_key: str = None) -> str:
    """Upload ke imgbb.com (kalau lo punya key gratis)"""
    if not api_key:
        return None
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    payload = {
        "key": api_key,
        "image": base64.b64encode(buffered.getvalue()).decode()
    }
    response = requests.post("https://api.imgbb.com/1/upload", data=payload)
    if response.status_code == 200:
        return response.json()["data"]["url"]
    return None

# --- Multi Upload Helper ---
def upload_references(face_files=None, pose_file=None, bg_file=None):
    """Upload semua reference, return dict URL"""
    references = {
        "face_urls": [],
        "pose_url": None,
        "bg_url": None
    }
    
    if face_files:
        for file in face_files:
            img = Image.open(file)
            url = upload_to_tmpfiles(img)
            if url:
                references["face_urls"].append(url)
    
    if pose_file:
        img = Image.open(pose_file)
        url = upload_to_tmpfiles(img)
        if url:
            references["pose_url"] = url
    
    if bg_file:
        img = Image.open(bg_file)
        url = upload_to_tmpfiles(img)
        if url:
            references["bg_url"] = url
    
    return references

# --- NSFW Prompt Enhancer (Auto Make More Detailed & Explicit) ---
def enhance_nsfw_prompt(prompt: str) -> str:
    """Tambah detail NSFW biar hasil lebih vivid & explicit"""
    enhancers = [
        ", highly detailed, sharp focus, 8k, cinematic lighting",
        ", explicit, nude, erotic pose, detailed anatomy",
        ", wet skin, sweat, aroused expression, bedroom eyes",
        ", masterpiece, best quality, ultra realistic"
    ]
    return prompt + " " + " ".join(enhancers)

# --- Animate Image to Video Fallback (Gratis Alternative kalau Fal habis) ---
def animate_with_perchance(image_url: str, motion_prompt: str = "smooth dancing, cinematic motion"):
    """Fallback animate via Perchance (manual link, karena no API)"""
    perchance_video_url = f"https://perchance.org/ai-text-to-video-generator?image={image_url}&prompt={motion_prompt}"
    return perchance_video_url

# --- Get NSFW Model List (Update Desember 2025) ---
def get_nsfw_models():
    return [
        "bytedance/seedream-5 (NSFW capable)",
        "fal-ai/flux-dev-lora",
        "pony-diffusion-v6-xl",
        "realistic-vision-v6-nsfw",
        "animagine-xl-3.1-nsfw",
        "anything-v5-nsfw"
  ]
