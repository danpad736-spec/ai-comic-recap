import os
import fitz  # PyMuPDF untuk konversi PDF ke gambar
from PIL import Image
import streamlit as st
from google import genai

# Konfigurasi halaman Streamlit
st.set_page_config(page_title="AI Comic Recap Generator", layout="wide")

st.title("🎬 AI Comic Recap Generator")
st.markdown("Unggah file PDF komik kamu, dan biarkan AI mengubahnya menjadi naskah video *recap* yang seru!")

# Input API Key dan File PDF di Sidebar
with st.sidebar:
    st.header("🔑 Konfigurasi")
    api_key_input = st.text_input("Masukkan Gemini API Key:", type="password")
    
    st.header("📂 Unggah File")
    uploaded_file = st.file_uploader("Pilih file PDF Komik", type=["pdf"])

if uploaded_file is not None and api_key_input:
    # Inisialisasi Gemini Client
    client = genai.Client(api_key=api_key_input)
    
    with st.spinner("🔄 Memproses halaman PDF komik..."):
        # Simpan file PDF sementara
        temp_pdf_path = "temp_comic.pdf"
        with open(temp_pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Konversi PDF halaman ke gambar
        doc = fitz.open(temp_pdf_path)
        images = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=150) # Resolusi cukup untuk dibaca AI
            img_path = f"temp_page_{page_num}.png"
            pix.save(img_path)
            images.append(Image.open(img_path))
        
        st.success(f"Berhasil memuat {len(images)} halaman komik!")

    # Tombol untuk generate naskah
    if st.button("🚀 Buat Naskah Recap Sekarang!", type="primary"):
        with st.spinner("🤖 AI sedang membaca komik dan meracik naskah video..."):
            try:
                # Prompt instruksi untuk AI
                prompt = (
                    "Bertindaklah sebagai penulis naskah profesional untuk channel YouTube Comic Recap. "
                    "Berdasarkan gambar-gambar halaman komik yang diunggah secara berurutan ini, buatkan naskah video recap yang lengkap: "
                    "1. Gunakan bahasa yang santai, memancing rasa penasaran, dramatis, dan asyik didengar. "
                    "2. Buat Hook/pembuka yang kuat di awal cerita. "
                    "3. Pecah naskah menjadi beberapa adegan (Scene 1, Scene 2, dst.) lengkap dengan narasi suara dan saran latar belakang musik (BGM) atau efek suara (SFX)."
                )
                
                # Gabungkan prompt dengan daftar gambar halaman komik
                contents = [prompt] + images
                
                # Panggil model Gemini
                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=contents
                )
                
                st.markdown("---")
                st.subheader("📜 Hasil Naskah Video Recap:")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
                
        # Bersihkan file sementara
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
else:
    if not api_key_input:
        st.info("👈 Silakan masukkan **Gemini API Key** di sidebar kiri untuk mulai.")
    elif not uploaded_file:
        st.info("📂 Silakan unggah file **PDF Komik** kamu di sidebar kiri.")
