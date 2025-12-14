import streamlit as st
from fal_client import FalClient
from PIL import Image
import requests
from io import BytesIO
import os

# --- Secrets (Paste di Streamlit Cloud Advanced Settings) ---
FAL_API_KEY = st.secrets.get("FAL_API_KEY")

if not FAL_API_KEY:
    st.error("FAL_API_KEY missing! Dapatkan gratis di fal.ai")
    st.stop()

client = FalClient(api_key=FAL_API_KEY)

st.set_page_config(page_title="NSFW GenAI Beast 2025", layout="wide")
st.title("🦾 Ultimate Uncensored NSFW GenAI Beast")
st.caption("Multi Face Ref + Pose + Background + Animate Video • Gratis Credit Fal.ai")

# --- Upload Multi Face Reference ---
st.subheader("Multi Face Reference (wajib untuk akurasi wajah)")
face_files = st.file_uploader("Upload 1-5 foto wajah karakter (semakin banyak semakin akurat)", type=["png","jpg","jpeg"], accept_multiple_files=True)

face_urls = []
if face_files:
    for file in face_files:
        img = Image.open(file)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = buffered.getvalue()
        # Upload temporary ke fal (atau imgbb, tapi fal support direct bytes)
        # Fal support multiple image inputs
        face_urls.append({"image": img_str, "weight": 1.0})

# --- Upload Pose Reference ---
st.subheader("Pose Reference (ControlNet OpenPose/Canny)")
pose_file = st.file_uploader("Upload gambar pose/gaya karakter (ControlNet)", type=["png","jpg"])

pose_url = None
if pose_file:
    img = Image.open(pose_file)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    pose_url = {"image": buffered.getvalue(), "controlnet": "openpose"}

# --- Upload Background Reference ---
st.subheader("Background Reference (IP-Adapter)")
bg_file = st.file_uploader("Upload background reference", type=["png","jpg"])

bg_url = None
if bg_file:
    img = Image.open(bg_file)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    bg_url = {"image": buffered.getvalue(), "adapter": "background"}

# --- Prompt & Model Choice ---
prompt = st.text_area("Prompt NSFW detail (explicit ok):", height=150)
negative_prompt = st.text_input("Negative prompt (optional):", "blurry, deformed, ugly")

model_options = [
    "flux-dev-lora" ,  # NSFW capable
    "sdxl-lightning",
    "pony-diffusion-v6",
    "realistic-vision-v6",
    "animagine-xl-3.1"  # anime NSFW beast
]
selected_model = st.selectbox("Pilih Model NSFW:", model_options)

if st.button("Generate NSFW Masterpiece"):
    if not prompt:
        st.error("Prompt wajib diisi")
    else:
        with st.spinner("Generating ultra accurate NSFW image..."):
            input_data = {
                "prompt": prompt,
                "negative_prompt": negative_prompt or "bad quality",
                "image_size": "portrait_9:16",
                "num_inference_steps": 28,
                "guidance_scale": 7.5,
                "sync": True
            }

            # Add multi face reference
            if face_urls:
                input_data["ip_adapter_image"] = face_urls  # fal support list

            # Add pose
            if pose_url:
                input_data["controlnet_image"] = pose_url["image"]
                input_data["controlnet_conditioning_scale"] = 1.0

            # Add background
            if bg_url:
                input_data["ip_adapter_background"] = bg_url["image"]

            result = client.run(f"fal-ai/{selected_model}", arguments=input_data)
            image_url = result["images"][0]["url"]

            st.image(image_url, caption="NSFW Result – Ultra Accurate Reference Match", use_column_width=True)

            # --- Animate to Video Button ---
            if st.button("Animate to Video (Image to Video NSFW)"):
                with st.spinner("Animating to NSFW video..."):
                    video_result = client.run("fal-ai/ltx-video", arguments={
                        "image_url": image_url,
                        "prompt": f"{prompt}, smooth motion, cinematic",
                        "duration": 5
                    })
                    video_url = video_result["video"]["url"]
                    st.video(video_url)
                    st.success("NSFW Video selesai – full motion dari reference lo!")

