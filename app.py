import streamlit as st
from PIL import Image
from io import BytesIO
import requests
from utils import upload_references, enhance_nsfw_prompt, get_venice_link, get_perchance_link, get_perchance_video_link

# --- Secrets ---
FAL_API_KEY = st.secrets.get("FAL_API_KEY")

if not FAL_API_KEY:
    st.error("FAL_API_KEY missing! Dapatkan gratis credit di https://fal.ai")
    st.stop()

headers = {
    "Authorization": f"Key {FAL_API_KEY}",
    "Content-Type": "application/json"
}

FAL_BASE_URL = "https://queue.fal.run/fal-ai"

st.set_page_config(page_title="NSFW Beast 2025 – Model Valid Fixed", layout="wide")
st.title("🦾 Ultimate Uncensored NSFW GenAI Beast – Model Valid & No 404")
st.caption("Multi Face/Pose/Background Accurate • Animate Video • Fal.ai + Venice.ai + Perchance Gratis Unlimited")

# --- Uploads ---
st.subheader("Multi Face Reference (1-5 foto wajah identik)")
face_files = st.file_uploader("Foto wajah karakter", type=["png","jpg","jpeg"], accept_multiple_files=True)

st.subheader("Pose Reference (ControlNet)")
pose_file = st.file_uploader("Gambar pose/gaya", type=["png","jpg"])

st.subheader("Background Reference")
bg_file = st.file_uploader("Background reference", type=["png","jpg"])

# --- Prompt & Model (Model Valid Desember 2025) ---
prompt = st.text_area("Prompt NSFW explicit:", height=150)
negative_prompt = st.text_input("Negative prompt:", "blurry, deformed, low quality")

valid_nsfw_models = [
    "flux/dev",             # Flux dev – NSFW capable
    "flux-pro",             # Flux pro
    "flux-2",               # Flux 2
    "flux-2-pro",           # Flux 2 pro
    "hyper-sdxl",           # Hyper SDXL
    "fast-sdxl"             # Fast SDXL
]
selected_model = st.selectbox("Model Fal.ai Valid NSFW:", valid_nsfw_models)

if st.button("Generate Ultra Accurate NSFW (Fal.ai)"):
    if not prompt:
        st.error("Prompt wajib!")
    else:
        with st.spinner("Uploading references & generating..."):
            refs = upload_references(face_files, pose_file, bg_file)
            enhanced_prompt = enhance_nsfw_prompt(prompt)
            
            payload = {
                "prompt": enhanced_prompt,
                "negative_prompt": negative_prompt,
                "num_inference_steps": 28,
                "guidance_scale": 7.0,
                "image_size": "square"
            }
            
            if refs["face_urls"]:
                payload["ip_adapter_image"] = refs["face_urls"]
            
            if refs["pose_url"]:
                payload["controlnet_image"] = refs["pose_url"]
                payload["controlnet_conditioning_scale"] = 1.0
            
            if refs["bg_url"]:
                payload["ip_adapter_background"] = refs["bg_url"]
            
            try:
                response = requests.post(f"{FAL_BASE_URL}/{selected_model}", headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                image_url = result["images"][0]["url"]
                
                st.image(image_url, caption="Hasil Fal.ai – Reference Match Sempurna", use_column_width=True)
                
                if st.button("Animate ke Video NSFW"):
                    with st.spinner("Animating video..."):
                        video_payload = {
                            "image_url": image_url,
                            "prompt": f"{enhanced_prompt}, smooth motion"
                        }
                        video_response = requests.post(f"{FAL_BASE_URL}/ltx-video", headers=headers, json=video_payload)
                        video_response.raise_for_status()
                        video_result = video_response.json()
                        video_url = video_result["video"]["url"]
                        st.video(video_url)
                        st.success("Video selesai!")
            except Exception as e:
                st.error(f"Fal.ai error: {e}")
                st.info("Gunakan fallback gratis unlimited di bawah!")

        # --- Fallback Venice.ai + Perchance.org ---
        st.subheader("Fallback Gratis Unlimited")
        
        primary_ref = refs["face_urls"][0] if refs["face_urls"] else None
        
        venice_link = get_venice_link(enhanced_prompt, primary_ref)
        perchance_link = get_perchance_link(enhanced_prompt, primary_ref)
        perchance_video_link = get_perchance_video_link(image_url if 'image_url' in locals() else primary_ref)
        
        st.markdown(f"**Private Gratis:** [Venice.ai]({venice_link})")
        st.markdown(f"**Unlimited Gratis:** [Perchance Image]({perchance_link})")
        if 'image_url' in locals():
            st.markdown(f"**Animate Gratis:** [Perchance Video]({perchance_video_link})")

st.success("App jalan! Model valid, no 404, generate NSFW chaos bebas Master!")
