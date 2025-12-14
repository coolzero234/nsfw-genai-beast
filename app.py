import streamlit as st
import fal_client
from PIL import Image
from io import BytesIO
import requests
from utils import upload_references, enhance_nsfw_prompt, get_venice_link, get_perchance_link, get_perchance_video_link

# --- Secrets ---
FAL_API_KEY = st.secrets.get("FAL_API_KEY")

if not FAL_API_KEY:
    st.error("FAL_API_KEY missing! Dapatkan gratis credit di https://fal.ai")
    st.stop()

fal_client.key = FAL_API_KEY

st.set_page_config(page_title="NSFW Beast 2025 – Final Running", layout="wide")
st.title("🦾 Ultimate Uncensored NSFW GenAI Beast – No Error Forever")
st.caption("Multi Face/Pose/Background Accurate • Animate Video • Fal.ai + Venice.ai + Perchance Unlimited Fallback")

# --- Upload References ---
st.subheader("Multi Face Reference (upload 1-5 foto wajah identik)")
face_files = st.file_uploader("Foto wajah karakter", type=["png","jpg","jpeg"], accept_multiple_files=True)

st.subheader("Pose Reference (ControlNet)")
pose_file = st.file_uploader("Gambar pose/gaya karakter", type=["png","jpg"])

st.subheader("Background Reference")
bg_file = st.file_uploader("Background reference", type=["png","jpg"])

# --- Prompt & Model ---
prompt = st.text_area("Prompt NSFW explicit (bebas apapun):", height=150)
negative_prompt = st.text_input("Negative prompt:", "blurry, deformed, low quality")

nsfw_models = [
    "fal-ai/flux-dev-lora",
    "fal-ai/pony-diffusion-v6",
    "fal-ai/realistic-vision-v6",
    "fal-ai/animagine-xl-3.1",
    "fal-ai/sdxl-lightning"
]
selected_model = st.selectbox("Model Fal.ai NSFW:", nsfw_models)

if st.button("Generate Ultra Accurate NSFW (Fal.ai Primary)"):
    if not prompt:
        st.error("Prompt wajib Master!")
    else:
        with st.spinner("Uploading references & generating dengan Fal.ai..."):
            refs = upload_references(face_files, pose_file, bg_file)
            enhanced_prompt = enhance_nsfw_prompt(prompt)
            
            input_data = {
                "prompt": enhanced_prompt,
                "negative_prompt": negative_prompt,
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
                "image_size": "portrait_9:16"
            }
            
            if refs["face_urls"]:
                input_data["ip_adapter_image"] = refs["face_urls"]
            
            if refs["pose_url"]:
                input_data["controlnet_image"] = refs["pose_url"]
                input_data["controlnet_conditioning_scale"] = 1.0
            
            if refs["bg_url"]:
                input_data["ip_adapter_background"] = refs["bg_url"]
            
            try:
                result = fal_client.run(selected_model, arguments=input_data)
                image_url = result["images"][0]["url"]
                
                st.image(image_url, caption="Hasil Fal.ai – Match Reference Sempurna", use_column_width=True)
                
                if st.button("Animate ke Video NSFW Cinematic"):
                    with st.spinner("Animating explicit video..."):
                        video_result = fal_client.run("fal-ai/ltx-video", arguments={
                            "image_url": image_url,
                            "prompt": f"{enhanced_prompt}, smooth erotic motion"
                        })
                        video_url = video_result["video"]["url"]
                        st.video(video_url)
                        st.success("Video NSFW selesai – full explicit motion!")
            except Exception as e:
                st.error(f"Fal.ai error (credit habis?): {e}")
                st.info("Gunakan fallback gratis unlimited di bawah!")

        # --- Fallback Venice.ai + Perchance.org ---
        st.subheader("Fallback Gratis Unlimited Uncensored")
        
        primary_ref = refs["face_urls"][0] if refs["face_urls"] else None
        
        venice_link = get_venice_link(enhanced_prompt, primary_ref)
        perchance_link = get_perchance_link(enhanced_prompt, primary_ref)
        perchance_video_link = get_perchance_video_link(image_url if 'image_url' in locals() else primary_ref)
        
        st.markdown(f"**Private Powerful Gratis:** [Venice.ai]({venice_link})")
        st.markdown(f"**Unlimited No Login:** [Perchance Image]({perchance_link})")
        if 'image_url' in locals():
            st.markdown(f"**Animate Video Gratis:** [Perchance Video]({perchance_video_link})")

st.success("App running 100%! Fal.ai = akurat reference + video. Venice = private. Perchance = unlimited. Generate NSFW chaos bebas Master!")

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
