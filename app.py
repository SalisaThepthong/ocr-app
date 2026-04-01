import streamlit as st
import pytesseract
import cv2
import numpy as np
import pandas as pd
import re
from pdf2image import convert_from_bytes

st.title("📄 OCR Shopee Order (Batch Processing)")

# CONFIG
BATCH_SIZE = 10
MAX_PAGES = 15

# ----------------------
# SESSION STATE
# ----------------------
if "results" not in st.session_state:
    st.session_state.results = []

if "processed_files" not in st.session_state:
    st.session_state.processed_files = 0

# ----------------------
# FUNCTION
# ----------------------
def extract_orders(text, page, file_name):
    matches = re.findall(
        r'Sho?ppee?\s*Order\s*N[o0]\.?\s*[:\-]?\s*([A-Z0-9]+)',
        text,
        re.IGNORECASE
    )

    return [{
        "Order Number": m.upper(),
        "Page": page,
        "File": file_name
    } for m in matches]

# ----------------------
# UPLOAD
# ----------------------
uploaded_files = st.file_uploader(
    "📤 อัปโหลด PDF (หลายไฟล์)",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:

    total_files = len(uploaded_files)
    st.info(f"📦 จำนวนไฟล์ทั้งหมด: {total_files}")

    # แบ่ง batch
    batches = [uploaded_files[i:i+BATCH_SIZE] 
               for i in range(0, total_files, BATCH_SIZE)]

    st.write(f"🔄 แบ่งเป็น {len(batches)} batch")

    # ----------------------
    # PROCESS BUTTON
    # ----------------------
    if st.button("🚀 เริ่มประมวลผล"):

        progress = st.progress(0)

        for batch_index, batch in enumerate(batches):

            st.write(f"📦 Batch {batch_index+1}/{len(batches)}")

            for uploaded_file in batch:

                try:
                    images = convert_from_bytes(
                        uploaded_file.read(),
                        dpi=100,
                        first_page=1,
                        last_page=MAX_PAGES
                    )
                except Exception as e:
                    st.error(f"❌ อ่านไฟล์ {uploaded_file.name} ไม่ได้")
                    continue

                for i, page in enumerate(images):

                    img = np.array(page)
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

                    text = pytesseract.image_to_string(thresh)

                    results = extract_orders(
                        text,
                        i+1,
                        uploaded_file.name
                    )

                    st.session_state.results.extend(results)

                st.session_state.processed_files += 1

            progress.progress((batch_index+1)/len(batches))

        st.success("✅ ประมวลผลครบแล้ว!")

# ----------------------
# RESULT
# ----------------------
st.subheader("📊 ผลลัพธ์สะสม")

if st.session_state.results:

    df = pd.DataFrame(st.session_state.results).drop_duplicates()

    st.write(f"📦 ประมวลผลแล้ว: {st.session_state.processed_files} ไฟล์")
    st.dataframe(df)

    file_name = "orders.xlsx"
    df.to_excel(file_name, index=False)

    with open(file_name, "rb") as f:
        st.download_button("📥 Download Excel", f, file_name)

# ----------------------
# RESET
# ----------------------
if st.button("🗑️ เคลียร์ข้อมูล"):
    st.session_state.results = []
    st.session_state.processed_files = 0
    st.success("ล้างข้อมูลแล้ว")