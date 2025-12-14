import streamlit as st
from PIL import Image
from io import BytesIO
import requests
from utils import upload_references, enhance_nsfw_prompt, get_venice_link, get_perchance_link, get_perchance_video_link

# --- Secrets ---
FAL_API_KEY = st.secrets.get("FAL_API_KEY")

if not FAL_API_KEY:
    st.error("FAL_API_KEY missing! Dapatkan di https://fal.ai")
    st.stop()

headers = {
    "Authorization": f"Key {FAL_API_KEY}",
    "Content-Type": "application/json"
}

FAL_BASE_URL = "https://queue.fal.run/fal-ai"

st.set_page_config(page_title="Ultimate NSFW Beast 2025", layout="wide")
st.title("🦾 Ultimate Uncensored NSFW GenAI Beast – All Fitur + Fallback Gratis")
st.caption("Multi Face/Pose/Background Accurate • Animate Video • Fal.ai + Venice.ai + Perchance Unlimited")

# --- Uploads Multi Reference ---
st.subheader("Multi Face Reference (upload 1-5 foto untuk wajah identik)")
face_files = st.file_uploader("Foto wajah karakter", type=["png","jpg","jpeg"], accept_multiple_files=True)

st.subheader("Pose Reference (ControlNet)")
pose_file = st.file_uploader("Gambar pose/gaya karakter", type=["png","jpg"])

st.subheader("Background Reference (IP-Adapter)")
bg_file = st.file_uploader("Background reference", type=["png","jpg"])

# --- Prompt & Model Choice ---
prompt = st.text_area("Prompt NSFW explicit (bebas apapun):", height=150)
negative_prompt = st.text_input("Negative prompt:", "blurry, deformed, low quality, bad anatomy")

nsfw_models = [
    "flux-dev-lora",
    "pony-diffusion-v6",
    "realistic-vision-v6",
    "animagine-xl-3.1",
    "hyper-sdxl",
    "sdxl-lightning"
]
selected_model = st.selectbox("Model Fal.ai NSFW Uncensored:", nsfw_models)

if st.button("Generate Ultra Accurate NSFW (Fal.ai)"):
    if not prompt:
        st.error("Prompt wajib Master!")
    else:
        with st.spinner("Uploading references & generating NSFW masterpiece..."):
            refs = upload_references(face_files, pose_file, bg_file)
            enhanced_prompt = enhance_nsfw_prompt(prompt)
            
            payload = {
                "prompt": enhanced_prompt,
                "negative_prompt": negative_prompt,
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
                "image_size": "portrait_9:16"
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
                
                st.image(image_url, caption="Hasil Fal.ai – Wajah/Pose/Background Match Sempurna", use_column_width=True)
                
                if st.button("Animate ke Video NSFW Cinematic"):
                    with st.spinner("Animating explicit video..."):
                        video_payload = {
                            "image_url": image_url,
                            "prompt": f"{enhanced_prompt}, smooth erotic motion, high detail"
                        }
                        video_response = requests.post(f"{FAL_BASE_URL}/ltx-video", headers=headers, json=video_payload)
                        video_response.raise_for_status()
                        video_result = video_response.json()
                        video_url = video_result["video"]["url"]
                        st.video(video_url)
                        st.success("Video NSFW selesai – full explicit motion!")
            except Exception as e:
                st.error(f"Fal.ai gagal (credit habis?): {e}")
                st.info("Langsung pakai fallback gratis unlimited di bawah!")

        # --- Fallback Venice.ai + Perchance.org ---
        st.subheader("Fallback Gratis Unlimited Uncensored")
        
        primary_ref = refs["face_urls"][0] if refs["face_urls"] else None
        
        venice_link = get_venice_link(enhanced_prompt, primary_ref)
        perchance_link = get_perchance_link(enhanced_prompt, primary_ref)
        perchance_video_link = get_perchance_video_link(image_url if 'image_url' in locals() else primary_ref)
        
        st.markdown(f"**Private & Powerful Gratis:** [Venice.ai]({venice_link})")
        st.markdown(f"**Unlimited No Login:** [Perchance Image]({perchance_link})")
        if 'image_url' in locals():
            st.markdown(f"**Animate Video Gratis:** [Perchance Video]({perchance_video_link})")

st.success("App jalan perfect! Fal.ai = akurat reference + video. Venice = private. Perchance = unlimited. Generate NSFW chaos bebas selamanya Master!")
