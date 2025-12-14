import streamlit as st
import fal_client

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
           print(log["message"])

result = fal_client.subscribe(
    "fal-ai/flux/dev",
    arguments={
        "prompt": "Extreme close-up of a single tiger eye, direct frontal view. Detailed iris and pupil. Sharp focus on eye texture and color. Natural lighting to capture authentic eye shine and depth. The word \"FLUX\" is painted over it in big, white brush strokes with visible texture."
    },
    with_logs=True,
    on_queue_update=on_queue_update,
)
print(result)
from PIL import Image
from io import BytesIO
import requests
from utils import upload_references, enhance_nsfw_prompt, get_venice_link, get_perchance_link, get_perchance_video_link

# --- Secrets ---
FAL_API_KEY = st.secrets.get("FAL_API_KEY")

if not FAL_API_KEY:
    st.error("FAL_API_KEY missing! Dapatkan gratis credit di fal.ai")
    st.stop()

fal_client.key = FAL_API_KEY

st.set_page_config(page_title="Ultimate NSFW Beast 2025", layout="wide")
st.title("🦾 Ultimate Uncensored NSFW GenAI Beast")
st.caption("Multi Reference Accurate • Animate Video • Fal.ai + Venice.ai + Perchance Fallback Gratis Unlimited")

# --- Upload References ---
st.subheader("Multi Face Reference (1-5 foto untuk wajah identik)")
face_files = st.file_uploader("Upload foto wajah karakter", type=["png","jpg","jpeg"], accept_multiple_files=True)

st.subheader("Pose Reference (ControlNet)")
pose_file = st.file_uploader("Upload gambar pose/gaya", type=["png","jpg"])

st.subheader("Background Reference")
bg_file = st.file_uploader("Upload background reference", type=["png","jpg"])

# --- Prompt & Model ---
prompt = st.text_area("Prompt NSFW explicit (apa aja ok):", height=150)
negative_prompt = st.text_input("Negative prompt:", "blurry, deformed, low quality, bad anatomy")

nsfw_models = [
    "fal-ai/flux-dev-lora",
    "fal-ai/pony-diffusion-v6",
    "fal-ai/realistic-vision-v6",
    "fal-ai/animagine-xl-3.1",
    "fal-ai/sdxl-lightning"
]
selected_model = st.selectbox("Model Fal.ai NSFW Uncensored:", nsfw_models)

if st.button("Generate Ultra Accurate NSFW (Fal.ai)"):
    if not prompt:
        st.error("Prompt wajib diisi!")
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
                
                st.image(image_url, caption="Hasil Fal.ai – Wajah/Pose/Background Super Akurat", use_column_width=True)
                
                # Animate Video Button
                if st.button("Animate ke Video NSFW Cinematic"):
                    with st.spinner("Animating video explicit..."):
                        video_result = fal_client.run("fal-ai/ltx-video", arguments={
                            "image_url": image_url,
                            "prompt": f"{enhanced_prompt}, smooth erotic motion, high detail"
                        })
                        video_url = video_result["video"]["url"]
                        st.video(video_url)
                        st.success("Video NSFW selesai – full explicit motion!")
                        
            except Exception as e:
                st.error(f"Fal.ai error (mungkin credit habis): {e}")
                st.info("Gunakan fallback gratis di bawah ini!")

        # --- Fallback Venice.ai + Perchance.org ---
        st.subheader("Fallback Gratis Unlimited Uncensored")
        
        primary_ref = refs["face_urls"][0] if refs["face_urls"] else None
        
        venice_link = get_venice_link(enhanced_prompt, primary_ref)
        perchance_link = get_perchance_link(enhanced_prompt, primary_ref)
        perchance_video_link = get_perchance_video_link(image_url if 'image_url' in locals() else primary_ref)
        
        st.markdown(f"**Generate Gratis Powerful & Private:** [Venice.ai]({venice_link})")
        st.markdown(f"**Generate Unlimited No Login:** [Perchance.org Image]({perchance_link})")
        if 'image_url' in locals():
            st.markdown(f"**Animate Gratis ke Video:** [Perchance.org Video]({perchance_video_link})")

st.info("Fal.ai = akurat multi reference + video. Venice.ai = private powerful. Perchance = unlimited gratis no filter. Pilih sesuai kebutuhan Master!")
