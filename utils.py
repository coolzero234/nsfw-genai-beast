import requests
from PIL import Image
from io import BytesIO
import streamlit as st

# --- Upload ke Tmpfiles.org (Gratis, No Key, No NSFW Filter, Direct Link) ---
def upload_to_tmpfiles(image: Image.Image) -> str:
    """Upload image & return direct URL (tmpfiles.org - uncensored NSFW friendly)"""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    buffered.seek(0)
    
    files = {'file': ('nsfw_ref.png', buffered, 'image/png')}
    try:
        response = requests.post("https://tmpfiles.org/api/v1/upload", files=files, timeout=30)
        if response.status_code == 200:
            data = response.json()["data"]
            full_url = data["url"]
            # Convert ke direct download link
            direct_url = full_url.replace("/dl/", "/")
            return direct_url
    except Exception as e:
        st.warning(f"Upload gagal: {e}")
    return None

# --- Multi Reference Upload Handler ---
def upload_references(face_files=None, pose_file=None, bg_file=None):
    """Upload semua reference, return dict URL untuk Fal.ai / other API"""
    refs = {
        "face_urls": [],
        "pose_url": None,
        "bg_url": None
    }
    
    if face_files:
        st.info(f"Uploading {len(face_files)} face references...")
        for i, file in enumerate(face_files):
            img = Image.open(file)
            url = upload_to_tmpfiles(img)
            if url:
                refs["face_urls"].append(url)
                st.success(f"Face ref {i+1} uploaded: {url}")
    
    if pose_file:
        st.info("Uploading pose reference...")
        img = Image.open(pose_file)
        url = upload_to_tmpfiles(img)
        if url:
            refs["pose_url"] = url
            st.success(f"Pose ref uploaded: {url}")
    
    if bg_file:
        st.info("Uploading background reference...")
        img = Image.open(bg_file)
        url = upload_to_tmpfiles(img)
        if url:
            refs["bg_url"] = url
            st.success(f"Background ref uploaded: {url}")
    
    return refs

# --- NSFW Prompt Auto Enhancer (More Explicit & Detailed) ---
def enhance_nsfw_prompt(prompt: str) -> str:
    """Auto tambah detail NSFW biar hasil lebih vivid, explicit, high quality"""
    nsfw_boosters = [
        ", highly detailed anatomy",
        ", sharp focus, 8k resolution",
        ", cinematic lighting, dramatic shadows",
        ", wet skin, sweat droplets",
        ", aroused expression, bedroom eyes",
        ", masterpiece, best quality, ultra realistic",
        ", explicit, no censorship"
    ]
    return prompt + " " + " ".join(nsfw_boosters)

# --- Fallback Perchance Animate Link (Kalau Fal Video Habis Credit) ---
def get_perchance_animate_link(image_url: str, motion_prompt: str = "smooth erotic dancing, cinematic camera movement"):
    """Return Perchance video gen link sebagai fallback gratis"""
    base = "https://perchance.org/ai-text-to-video-generator"
    params = f"?image={image_url}&prompt={motion_prompt.replace(' ', '%20')}"
    return base + params

# --- More NSFW Model Suggestions ---
def get_more_nsfw_models():
    return [
        "fal-ai/flux-dev-lora",
        "fal-ai/pony-diffusion-v6",
        "fal-ai/realistic-vision-v6",
        "fal-ai/animagine-xl-3.1",
        "fal-ai/hyper-sdxl"
            ]

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

def get_perchance_video_link(image_url: str, motion_prompt: str = "smooth dancing, cinematic camera"):
    return f"https://perchance.org/ai-text-to-video-generator?image={image_url}&prompt={motion_prompt.replace(' ', '%20')}"
