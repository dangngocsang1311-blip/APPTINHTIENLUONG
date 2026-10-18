import streamlit as st
import os
st.image("LOGO.jpg")
import pandas as pd
import plotly.express as px

# Cấu hình trang
st.set_page_config(page_title="PHẦN MỀM TÍNH TIỀN LƯƠNG HV ĐẶNG NGỌC SANG", page_icon="💰", layout="centered")

st.title("PHẦN MỀM TÍNH TIỀN LƯƠNG HV ĐẶNG NGỌC SANG")
st.markdown("Nhập các thông số thu nhập bên dưới (Đơn vị: Triệu đồng). Kết quả sẽ tự động tính toán.")
st.markdown("---")

# Khung nhập liệu
col1, col2 = st.columns(2)

with col1:
    LUONGCOBAN = st.number_input("TIỀN LƯƠNG CƠ BẢN", min_value=0.0, value=15.0, step=1.0)
    THUONG = st.number_input("TIỀN THƯỞNG", min_value=0.0, value=2.0, step=1.0)
    PHUCAPCOBHXH = st.number_input("PHỤ CẤP CÓ TÍNH BHXH", min_value=0.0, value=3.0, step=1.0)

with col2:
    PHUCAPKHONGBHXH = st.number_input("PHỤ CẤP KHÔNG TÍNH BHXH", min_value=0.0, value=1.0, step=1.0)
    SONGUOIPHUTHUOC = st.number_input("SỐ NGƯỜI PHỤ THUỘC", min_value=0, value=1, step=1)

# Logic tính toán (Dựa trên code gốc, bổ sung chặn số âm)
TONGTHUNHAP = LUONGCOBAN + THUONG + PHUCAPCOBHXH + PHUCAPKHONGBHXH
TIENDONGBHXH = (LUONGCOBAN + PHUCAPCOBHXH) * 0.105

# Tránh trường hợp thu nhập tính thuế bị âm khi tổng giảm trừ lớn hơn thu nhập
THUNHAPTINHTHUETNCN = max(0, TONGTHUNHAP - 15.5 - (6.2 * SONGUOIPHUTHUOC) - TIENDONGBHXH)

# Tính thuế theo 5 bậc
if THUNHAPTINHTHUETNCN <= 10:
    THUETNCN = THUNHAPTINHTHUETNCN * 0.05
elif THUNHAPTINHTHUETNCN <= 30:
    THUETNCN = THUNHAPTINHTHUETNCN * 0.1 - 0.5
elif THUNHAPTINHTHUETNCN <= 60:
    THUETNCN = THUNHAPTINHTHUETNCN * 0.2 - 3.5 
elif THUNHAPTINHTHUETNCN <= 100:
    THUETNCN = THUNHAPTINHTHUETNCN * 0.3 - 9.5
else:
    THUETNCN = THUNHAPTINHTHUETNCN * 0.35 - 14.5

# Đảm bảo thuế không bị âm
THUETNCN = max(0, THUETNCN)

# Thực lãnh
THUCLANH = TONGTHUNHAP - TIENDONGBHXH - THUETNCN

# Hiển thị Kết quả
st.markdown("### 📊 Kết Quả Phân Bổ Dòng Tiền")

# Các thẻ chỉ số nổi bật
m1, m2, m3 = st.columns(3)
m1.metric("Tiền Đóng BHXH", f"{TIENDONGBHXH:,.2f} Tr")
m2.metric("Thuế TNCN", f"{THUETNCN:,.2f} Tr")
m3.metric("Thu Nhập Tính Thuế", f"{THUNHAPTINHTHUETNCN:,.2f} Tr")

st.success(f"**SỐ TIỀN THỰC LÃNH LÀ: {THUCLANH:,.2f} TRIỆU ĐỒNG**")

# Biểu đồ trực quan bằng Plotly
df_chart = pd.DataFrame({
    "Khoản tiền": ["Thực lãnh", "Tiền đóng BHXH", "Thuế TNCN"],
    "Giá trị (Triệu VNĐ)": [THUCLANH, TIENDONGBHXH, THUETNCN]
})

fig = px.pie(
    df_chart, 
    values="Giá trị (Triệu VNĐ)", 
    names="Khoản tiền", 
    hole=0.4,
    color="Khoản tiền",
    color_discrete_map={
        "Thực lãnh": "#27ae60",
        "Tiền đóng BHXH": "#2980b9",
        "Thuế TNCN": "#e74c3c"
    }
)
fig.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig, use_container_width=True)
