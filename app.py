import streamlit as st
import pytesseract
import cv2
import numpy as np
import pandas as pd
import re
from PIL import Image
from pdf2image import convert_from_bytes

st.set_page_config(page_title="OCR Order Reader", layout="centered")

st.title("📄 OCR ใบแปะหน้า (PDF รองรับหลายหน้า)")
st.write("อัปโหลด PDF / รูป → ดึงเลข Order → Export Excel")

# ----------------------
# OCR FUNCTION
# ----------------------
def extract_orders_from_image(image, page_num):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    text = pytesseract.image_to_string(thresh)

    matches = re.findall(
        r'Sho?ppee?\s*Order\s*N[o0]\.?\s*[:\-]?\s*([A-Z0-9]+)',
        text,
        re.IGNORECASE
    )

    results = []
    for order in matches:
        results.append({
            "Order Number": order.upper(),  # กันพลาด lowercase
            "Page": page_num
        })

    return results
# มันรองรับ:

# Shopee Order No. 123456
# Shopee Order No: 123456
# ShopeeOrderNo 123456
# เว้นวรรคมั่ว ๆ ก็ยังจับได้
# ----------------------
# FILE UPLOAD
# ----------------------
uploaded_file = st.file_uploader(
    "📤 อัปโหลดไฟล์",
    type=["jpg", "jpeg", "png", "pdf"]
)

if uploaded_file:
    all_orders = []

    with st.spinner("🔍 กำลังประมวลผล... (PDF ใหญ่จะใช้เวลา)"):
        
        # ----------------------
        # PDF CASE
        # ----------------------
        if uploaded_file.type == "application/pdf":
            pages = convert_from_bytes(uploaded_file.read())

            st.info(f"📄 จำนวนหน้า: {len(pages)}")

            for i, page in enumerate(pages):
                st.write(f"กำลังอ่านหน้า {i+1}...")
                results = extract_orders_from_image(page, i+1)
                all_orders.extend(results)

        # ----------------------
        # IMAGE CASE
        # ----------------------
        else:
            image = Image.open(uploaded_file)
            st.image(image, caption="📸 ภาพที่อัปโหลด")

            results = extract_orders_from_image(image, 1)
            all_orders.extend(results)

    # ----------------------
    # RESULT
    # ----------------------
    st.subheader("📦 Order ที่พบ")

    if all_orders:
        df = pd.DataFrame(all_orders)

        # ลบ duplicate (optional)
        df = df.drop_duplicates()

        st.dataframe(df, use_container_width=True)

        # Export Excel
        file_name = "orders.xlsx"
        df.to_excel(file_name, index=False)

        with open(file_name, "rb") as f:
            st.download_button(
                "📥 Download Excel",
                f,
                file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.warning("❌ ไม่พบ Order")