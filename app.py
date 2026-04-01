# import streamlit as st
# import pytesseract
# import cv2
# import numpy as np
# import pandas as pd
# import re
# from pdf2image import convert_from_bytes

# st.set_page_config(page_title="OCR Shopee Order", layout="centered")

# st.title("📄 OCR Shopee Order (Batch + PDF)")

# # ----------------------
# # CONFIG (ปรับได้)
# # ----------------------
# BATCH_SIZE = 5          # ไฟล์ต่อรอบ (กัน crash)
# MAX_PAGES = 10          # จำกัดหน้าต่อไฟล์
# DPI = 80                # ลดคุณภาพ → ประหยัด RAM

# # ----------------------
# # SESSION
# # ----------------------
# if "results" not in st.session_state:
#     st.session_state.results = []

# if "processed_files" not in st.session_state:
#     st.session_state.processed_files = 0

# # ----------------------
# # REGEX FUNCTION
# # ----------------------
# def extract_orders(text, page, file_name):
#     matches = re.findall(
#         r'Sho?ppee?\s*Order\s*N[o0]\.?\s*[:\-]?\s*([A-Z0-9]+)',
#         text,
#         re.IGNORECASE
#     )

#     return [{
#         "Order Number": m.upper(),
#         "Page": page,
#         "File": file_name
#     } for m in matches]

# # ----------------------
# # UPLOAD
# # ----------------------
# uploaded_files = st.file_uploader(
#     "📤 อัปโหลด PDF",
#     type=["pdf"],
#     accept_multiple_files=True
# )

# if uploaded_files:

#     st.info(f"📦 จำนวนไฟล์: {len(uploaded_files)}")

#     # แบ่ง batch
#     batches = [
#         uploaded_files[i:i+BATCH_SIZE]
#         for i in range(0, len(uploaded_files), BATCH_SIZE)
#     ]

#     st.write(f"🔄 แบ่งเป็น {len(batches)} batch")

#     # ----------------------
#     # PROCESS BUTTON
#     # ----------------------
#     if st.button("🚀 เริ่มประมวลผล"):

#         progress = st.progress(0)

#         for batch_index, batch in enumerate(batches):

#             st.write(f"📦 Batch {batch_index+1}/{len(batches)}")

#             for uploaded_file in batch:

#                 # 🔥 อ่านไฟล์ครั้งเดียว (สำคัญมาก)
#                 file_bytes = uploaded_file.read()

#                 try:
#                     images = convert_from_bytes(
#                         file_bytes,
#                         dpi=DPI,
#                         first_page=1,
#                         last_page=MAX_PAGES
#                     )
#                 except Exception as e:
#                     st.error(f"❌ อ่าน {uploaded_file.name} ไม่ได้")
#                     continue

#                 for i, page in enumerate(images):

#                     img = np.array(page)
#                     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#                     _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

#                     text = pytesseract.image_to_string(thresh)

#                     results = extract_orders(
#                         text,
#                         i+1,
#                         uploaded_file.name
#                     )

#                     st.session_state.results.extend(results)

#                 st.session_state.processed_files += 1

#             progress.progress((batch_index + 1) / len(batches))

#         st.success("✅ ประมวลผลครบแล้ว!")

# # ----------------------
# # RESULT
# # ----------------------
# st.subheader("📊 ผลลัพธ์")

# if st.session_state.results:

#     df = pd.DataFrame(st.session_state.results).drop_duplicates()

#     st.write(f"📦 ประมวลผลแล้ว: {st.session_state.processed_files} ไฟล์")

#     st.dataframe(df, width='stretch')

#     # Export Excel
#     file_name = "orders.xlsx"
#     df.to_excel(file_name, index=False)

#     with open(file_name, "rb") as f:
#         st.download_button(
#             "📥 Download Excel",
#             f,
#             file_name
#         )

# # ----------------------
# # RESET
# # ----------------------
# if st.button("🗑️ ล้างข้อมูล"):
#     st.session_state.results = []
#     st.session_state.processed_files = 0
#     st.success("ล้างข้อมูลแล้ว")
# app.py
import streamlit as st
import pdfplumber
import pandas as pd
import re

st.set_page_config(page_title="Order Extractor", layout="centered")
st.title("📄 Extract Order Number (Shopee / Lazada / TikTok)")

# ----------------------
# SESSION STATE
# ----------------------
if "results" not in st.session_state:
    st.session_state.results = []

# ----------------------
# FUNCTION: Extract Orders
# ----------------------
def extract_orders_from_text(text, page, file_name):
    results = []

    # Shopee
    shopee_matches = re.findall(
        r'Shopee\s*Order\s*No\.?\s*[:\-]?\s*([A-Z0-9]+)',
        text,
        re.IGNORECASE
    )
    for m in shopee_matches:
        results.append({
            "Page": page,
            "Order Number": m,
            "Platform": "Shopee",
            "File": file_name
        })

    # Lazada
    lazada_matches = re.findall(
        r'(?:Lazada\s*)?Order\s*(?:No\.?|Number|ID)?\s*[:\-]?\s*([A-Z0-9]{10,})',
        text,
        re.IGNORECASE
    )
    for m in lazada_matches:
        results.append({
            "Page": page,
            "Order Number": m,
            "Platform": "Lazada",
            "File": file_name
        })

    # TikTok
    tiktok_matches = re.findall(
        r'Order\s*ID\s*[:\-]?\s*([0-9]+)',
        text,
        re.IGNORECASE
    )
    for m in tiktok_matches:
        results.append({
            "Page": page,
            "Order Number": m,
            "Platform": "TikTok",
            "File": file_name
        })

    return results

# ----------------------
# UPLOAD PDF
# ----------------------
uploaded_files = st.file_uploader(
    "📤 อัปโหลด PDF",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:

    st.info(f"📦 จำนวนไฟล์: {len(uploaded_files)}")

    if st.button("🚀 เริ่มประมวลผล"):
        results_all = []

        for uploaded_file in uploaded_files:
            st.write(f"📄 Processing: {uploaded_file.name}")
            with pdfplumber.open(uploaded_file) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        results_all.extend(
                            extract_orders_from_text(text, i+1, uploaded_file.name)
                        )

        if results_all:
            df = pd.DataFrame(results_all).drop_duplicates()
            st.session_state.results = df
            st.success("✅ ประมวลผลครบแล้ว!")

# ----------------------
# SHOW RESULTS & DOWNLOAD
# ----------------------
if not st.session_state.results.empty:
    st.subheader("📊 ผลลัพธ์")
    st.dataframe(st.session_state.results, use_container_width=True)

    # Export Excel
    file_name = "orders.xlsx"
    st.download_button(
        "📥 ดาวน์โหลด Excel",
        st.session_state.results.to_excel(index=False),
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ----------------------
# RESET
# ----------------------
if st.button("🗑️ ล้างข้อมูล"):
    st.session_state.results = pd.DataFrame()
    st.success("ล้างข้อมูลเรียบร้อยแล้ว")