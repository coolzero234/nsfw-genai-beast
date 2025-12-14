import streamlit as st
import fal_client 
from PIL import Image
from io import BytesIO
import requests
from utils import upload_references, enhance_nsfw_prompt  # Dari utils.py

# --- Secrets ---
FAL_API_KEY = st.secrets.get("FAL_API_KEY")

if not FAL_API_KEY:
    st.error("FAL_API_KEY missing! Dapatkan gratis credit di fal.ai")
    st.stop()

# fal_client setup (global atau direct run)
fal_client.key = FAL_API_KEY  # Simple way

st.set_page_config(page_title="NSFW Ultimate Beast 2025", layout="wide")
st.title("🦾 Uncensored NSFW GenAI Monster – Fixed & Running")
st.caption("Multi Face/Pose/Background Ref • Accurate Match • Animate Video • Fal.ai Power")

# --- Uploads ---
st.subheader("Multi Face Reference (1-5 foto untuk wajah identik)")
face_files = st.file_uploader("Upload foto wajah karakter", type=["png","jpg","jpeg"], accept_multiple_files=True)

st.subheader("Pose Reference (ControlNet)")
pose_file = st.file_uploader("Upload gambar pose/gaya", type=["png","jpg"])

st.subheader("Background Reference")
bg_file = st.file_uploader("Upload background", type=["png","jpg"])

# --- Prompt & Model ---
prompt = st.text_area("Prompt NSFW explicit (no filter):", height=150)
negative_prompt = st.text_input("Negative prompt:", "blurry, low quality, deformed")

nsfw_models = [
    "fal-ai/flux-dev-lora",
    "fal-ai/pony-diffusion-v6",
    "fal-ai/realistic-vision-v6",
    "fal-ai/animagine-xl-3.1",
    "fal-ai/sdxl-lightning"
]
selected_model = st.selectbox("Pilih Model NSFW Uncensored:", nsfw_models)

if st.button("Generate Ultra Accurate NSFW"):
    if not prompt:
        st.error("Prompt wajib!")
    else:
        with st.spinner("Uploading references & generating NSFW masterpiece..."):
            refs = upload_references(face_files, pose_file, bg_file)
            
            enhanced = enhance_nsfw_prompt(prompt)
            
            input_data = {
                "prompt": enhanced,
                "negative_prompt": negative_prompt,
                "num_inference_steps": 30,
                "guidance_scale": 7.0,
                "image_size": "square"
            }
            
            # Multi face ref (fal support list URL)
            if refs["face_urls"]:
                input_data["ip_adapter_image"] = refs["face_urls"]
            
            # Pose ControlNet
            if refs["pose_url"]:
                input_data["controlnet_image"] = refs["pose_url"]
                input_data["controlnet_conditioning_scale"] = 1.0
            
            # Background IP-Adapter
            if refs["bg_url"]:
                input_data["ip_adapter_background"] = refs["bg_url"]
            
            result = fal_client.run(selected_model, arguments=input_data)
            image_url = result["images"][0]["url"]
            
            st.image(image_url, caption="NSFW Result – Wajah/Pose/Background Super Akurat", use_column_width=True)
            
            # Animate Button
            if st.button("Animate Hasil ke Video NSFW (Image to Video)"):
                with st.spinner("Animating NSFW video cinematic..."):
                    video_result = fal_client.run("fal-ai/ltx-video", arguments={
                        "image_url": image_url,
                        "prompt": f"{enhanced}, smooth erotic motion, high quality"
                    })
                    video_url = video_result["video"]["url"]
                    st.video(video_url)
                    st.success("NSFW Video selesai – full motion explicit!")

from utils import upload_references, enhance_nsfw_prompt, get_nsfw_models

# Di dalam generate button
references = upload_references(face_files, pose_file, bg_file)

# Gunakan references["face_urls"] dll untuk prompt atau API
enhanced_prompt = enhance_nsfw_prompt(prompt)
