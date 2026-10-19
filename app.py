import os
import fitz  # PyMuPDF untuk konversi PDF ke gambar
from PIL import Image
import streamlit as st
import base64
from io import BytesIO

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Universal AI Comic Recap Generator", layout="wide")

st.title("🎬 Universal AI Comic Recap Generator")
st.markdown("Unggah PDF komik, pilih AI favoritmu (Gemini, Groq, OpenAI, Claude, DeepSeek, atau OpenRouter), lalu buat naskah video *recap*!")

# Fungsi bantu untuk konversi PIL Image ke Base64
def image_to_base64(pil_img):
    buffered = BytesIO()
    pil_img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Sidebar untuk Pemilihan AI dan API Key
with st.sidebar:
    st.header("🔑 Konfigurasi AI")
    
    # Pilihan Provider AI
    ai_provider = st.selectbox(
        "Pilih Penyedia AI:",
        [
            "Gemini (Google)", 
            "Groq (Llama Vision)", 
            "OpenAI (ChatGPT)", 
            "Claude (Anthropic)", 
            "DeepSeek", 
            "OpenRouter (Semua AI)"
        ]
    )
    
    api_key_input = st.text_input(f"Masukkan API Key {ai_provider}:", type="password")
    
    st.header("📂 Unggah File")
    uploaded_file = st.file_uploader("Pilih file PDF Komik", type=["pdf"])

# Pemrosesan Utama
if uploaded_file is not None and api_key_input:
    with st.spinner("🔄 Memproses halaman PDF komik..."):
        temp_pdf_path = "temp_comic.pdf"
        with open(temp_pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        doc = fitz.open(temp_pdf_path)
        images = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=150)
            img_path = f"temp_page_{page_num}.png"
            pix.save(img_path)
            images.append(Image.open(img_path))
        
        st.success(f"Berhasil memuat {len(images)} halaman komik!")

    prompt_text = (
        "Bertindaklah sebagai penulis naskah profesional untuk channel YouTube Comic Recap. "
        "Berdasarkan gambar-gambar halaman komik yang diunggah secara berurutan ini, buatkan naskah video recap yang lengkap: "
        "1. Gunakan bahasa yang santai, memancing rasa penasaran, dramatis, dan asyik didengar. "
        "2. Buat Hook/pembuka yang kuat di awal cerita. "
        "3. Pecah naskah menjadi beberapa adegan (Scene 1, Scene 2, dst.) lengkap dengan narasi suara dan saran latar belakang musik (BGM) atau efek suara (SFX)."
    )

    if st.button("🚀 Buat Naskah Recap Sekarang!", type="primary"):
        with st.spinner(f"🤖 {ai_provider} sedang meracik naskah..."):
            try:
                result_text = ""

                # --- 1. GEMINI (GOOGLE) ---
                if "Gemini" in ai_provider:
                    from google import genai
                    client = genai.Client(api_key=api_key_input)
                    contents = [prompt_text] + images
                    response = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=contents
                    )
                    result_text = response.text

                # --- 2. GROQ (LLAMA VISION) ---
                elif "Groq" in ai_provider:
                    from groq import Groq
                    client = Groq(api_key=api_key_input)
                    content_payload = [{"type": "text", "text": prompt_text}]
                    for img in images:
                        b64_img = image_to_base64(img)
                        content_payload.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}
                        })
                    response = client.chat.completions.create(
                        model="llama-3.2-11b-vision-instruct",
                        messages=[{"role": "user", "content": content_payload}]
                    )
                    result_text = response.choices[0].message.content

                # --- 3. OPENAI (CHATGPT) ---
                elif "OpenAI" in ai_provider:
                    from openai import OpenAI
                    client = OpenAI(api_key=api_key_input)
                    content_payload = [{"type": "text", "text": prompt_text}]
                    for img in images:
                        b64_img = image_to_base64(img)
                        content_payload.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}
                        })
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": content_payload}]
                    )
                    result_text = response.choices[0].message.content

                # --- 4. CLAUDE (ANTHROPIC) ---
                elif "Claude" in ai_provider:
                    import anthropic
                    client = anthropic.Anthropic(api_key=api_key_input)
                    content_payload = []
                    for img in images:
                        b64_img = image_to_base64(img)
                        content_payload.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": b64_img
                            }
                        })
                    content_payload.append({"type": "text", "text": prompt_text})
                    response = client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=4000,
                        messages=[{"role": "user", "content": content_payload}]
                    )
                    result_text = response.content[0].text

                # --- 5. DEEPSEEK ---
                elif "DeepSeek" in ai_provider:
                    from openai import OpenAI
                    client = OpenAI(
                        api_key=api_key_input,
                        base_url="https://api.deepseek.com"
                    )
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": "Bertindaklah sebagai penulis naskah profesional untuk channel YouTube Comic Recap."},
                            {"role": "user", "content": prompt_text}
                        ]
                    )
                    result_text = response.choices[0].message.content

                # --- 6. OPENROUTER ---
                elif "OpenRouter" in ai_provider:
                    from openai import OpenAI
                    client = OpenAI(
                        api_key=api_key_input,
                        base_url="https://openrouter.ai/api/v1"
                    )
                    content_payload = [{"type": "text", "text": prompt_text}]
                    for img in images:
                        b64_img = image_to_base64(img)
                        content_payload.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}
                        })
                    response = client.chat.completions.create(
                        model="google/gemini-2.0-flash-001",
                        messages=[{"role": "user", "content": content_payload}]
                    )
                    result_text = response.choices[0].message.content

                # Tampilkan Hasil
                st.markdown("---")
                st.subheader(f"📜 Hasil Naskah Video Recap ({ai_provider}):")
                st.markdown(result_text)

            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses dengan {ai_provider}: {e}")

        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
else:
    if not api_key_input:
        st.info("👈 Silakan pilih AI dan masukkan **API Key** yang sesuai di sidebar kiri.")
    elif not uploaded_file:
        st.info("📂 Silakan unggah file **PDF Komik** kamu di sidebar kiri.")
