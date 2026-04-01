import streamlit as st
import pytesseract
import cv2
import numpy as np
import pandas as pd
import re
from pdf2image import convert_from_bytes

st.title("📄 OCR Shopee Order (รองรับหลาย PDF)")

# CONFIG
MAX_FILES_PER_BATCH = 10
MAX_PAGES = 15

uploaded_files = st.file_uploader(
    "📤 อัปโหลด PDF (หลายไฟล์)",
    type=["pdf"],
    accept_multiple_files=True
)

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

if uploaded_files:

    all_results = []

    total_files = len(uploaded_files)
    st.info(f"📦 จำนวนไฟล์ทั้งหมด: {total_files}")

    # 🔥 แบ่ง batch
    batches = [uploaded_files[i:i + MAX_FILES_PER_BATCH] 
               for i in range(0, total_files, MAX_FILES_PER_BATCH)]

    progress = st.progress(0)

    for batch_index, batch in enumerate(batches):
        st.write(f"🚀 Batch {batch_index+1}/{len(batches)}")

        for uploaded_file in batch:

            images = convert_from_bytes(
                uploaded_file.read(),
                dpi=100,
                fmt="jpeg"
            )

            for i, page in enumerate(images):

                if i >= MAX_PAGES:
                    break

                img = np.array(page)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

                text = pytesseract.image_to_string(thresh)

                results = extract_orders(text, i+1, uploaded_file.name)
                all_results.extend(results)

        progress.progress((batch_index + 1) / len(batches))

    # RESULT
    st.subheader("📦 Order ทั้งหมด")

    if all_results:
        df = pd.DataFrame(all_results).drop_duplicates()

        st.dataframe(df)

        file_name = "orders.xlsx"
        df.to_excel(file_name, index=False)

        with open(file_name, "rb") as f:
            st.download_button("📥 Download Excel", f, file_name)
    else:
        st.warning("❌ ไม่พบ Order")