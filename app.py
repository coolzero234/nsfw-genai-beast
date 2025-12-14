import streamlit as st
import fal-ai/client  # Import benar – underscore setelah install fal-client
from PIL import Image
from io import BytesIO
import requests
from utils import upload_references, enhance_nsfw_prompt

# --- Secrets ---
FAL_API_KEY = st.secrets.get("FAL_API_KEY")

if not FAL_API_KEY:
    st.error("FAL_API_KEY missing! Dapatkan gratis credit besar di fal.ai")
    st.stop()

# Set global key
fal_client.key = FAL_API_KEY

st.set_page_config(page_title="NSFW Beast 2025 Final Fixed", layout="wide")
st.title("🦾 Ultimate Uncensored NSFW GenAI Monster – No More Errors")
st.caption("Multi Face/Pose/Background Accurate • Animate Video • Fal.ai Uncensored Power")

# --- Uploads Multi Reference ---
st.subheader("Multi Face Reference (upload 1-5 foto wajah untuk match identik)")
face_files = st.file_uploader("Foto wajah karakter", type=["png","jpg","jpeg"], accept_multiple_files=True)

st.subheader("Pose Reference (ControlNet OpenPose/Canny)")
pose_file = st.file_uploader("Gambar pose/gaya karakter", type=["png","jpg"])

st.subheader("Background Reference (IP-Adapter)")
bg_file = st.file_uploader("Background reference", type=["png","jpg"])

# --- Prompt & Model Choice ---
prompt = st.text_area("Prompt NSFW explicit (no filter, detail apapun ok):", height=150)
negative_prompt = st.text_input("Negative prompt (optional):", "blurry, deformed, bad anatomy, low quality")

nsfw_models = [
    "fal-ai/flux-dev-lora",           # NSFW ultra capable
    "fal-ai/pony-diffusion-v6",       # Pony NSFW beast
    "fal-ai/realistic-vision-v6",     # Realistic NSFW
    "fal-ai/animagine-xl-3.1",        # Anime NSFW
    "fal-ai/sdxl-lightning"           # Fast NSFW
]
selected_model = st.selectbox("Pilih Model Uncensored NSFW:", nsfw_models)

if st.button("Generate Ultra Accurate NSFW Masterpiece"):
    if not prompt:
        st.error("Prompt wajib diisi Master!")
    else:
        with st.spinner("Uploading references & generating explicit NSFW..."):
            refs = upload_references(face_files, pose_file, bg_file)
            
            enhanced_prompt = enhance_nsfw_prompt(prompt)
            
            input_data = {
                "prompt": enhanced_prompt,
                "negative_prompt": negative_prompt,
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
                "image_size": "portrait_9:16"
            }
            
            # Multi face IP-Adapter
            if refs["face_urls"]:
                input_data["ip_adapter_image"] = refs["face_urls"]  # List URL untuk multi face
            
            # Pose ControlNet
            if refs["pose_url"]:
                input_data["controlnet_image"] = refs["pose_url"]
                input_data["controlnet_conditioning_scale"] = 1.0
            
            # Background IP-Adapter
            if refs["bg_url"]:
                input_data["ip_adapter_background"] = refs["bg_url"]
            
            result = fal_client.run(selected_model, arguments=input_data)
            image_url = result["images"][0]["url"]
            
            st.image(image_url, caption="NSFW Result – Wajah/Pose/Background Match Sempurna", use_column_width=True)
            
            # Animate to Video Button
            if st.button("Animate ke Video NSFW Cinematic (Image to Video Explicit)"):
                with st.spinner("Animating explicit motion video..."):
                    video_result = fal_client.run("fal-ai/ltx-video", arguments={
                        "image_url": image_url,
                        "prompt": f"{enhanced_prompt}, smooth erotic movement, high detail"
                    })
                    video_url = video_result["video"]["url"]
                    st.video(video_url)
                    st.success("NSFW Video selesai – full explicit motion dari reference lo!")

from utils import upload_references, enhance_nsfw_prompt, get_nsfw_models

# Di dalam generate button
references = upload_references(face_files, pose_file, bg_file)

# Gunakan references["face_urls"] dll untuk prompt atau API
enhanced_prompt = enhance_nsfw_prompt(prompt)
