import streamlit as st
import pytesseract
import cv2
import numpy as np
import pandas as pd
import re
from PIL import Image

# ----------------------
# CONFIG
# ----------------------
st.set_page_config(page_title="OCR Order Reader", layout="centered")

st.title("📄 OCR ใบแปะหน้า")
st.write("อัปโหลดภาพ → ดึงเลข Order → Export Excel")

# ----------------------
# FUNCTION: OCR + Extract
# ----------------------
def extract_orders(image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ปรับภาพให้ชัดขึ้น
    gray = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    text = pytesseract.image_to_string(thresh)

    # 🔥 ปรับ regex ตาม format จริงได้
    orders = re.findall(r'\b\d{6,}\b', text)

    return text, list(set(orders))

# ----------------------
# UI
# ----------------------
uploaded_file = st.file_uploader(
    "📤 อัปโหลดใบแปะหน้า",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    image = Image.open(uploaded_file)

    st.image(image, caption="📸 ภาพที่อัปโหลด", use_container_width=True)

    with st.spinner("🔍 กำลังอ่านข้อมูล..."):
        text, orders = extract_orders(image)

    # แสดงข้อความ OCR
    with st.expander("📃 ดูข้อความทั้งหมด"):
        st.text(text)

    # แสดงผล Order
    st.subheader("📦 Order ที่พบ")

    if orders:
        df = pd.DataFrame(orders, columns=["Order Number"])
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