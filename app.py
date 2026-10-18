import streamlit as st
import os
import pandas as pd
import plotly.express as px
from io import BytesIO

# 1. CẤU HÌNH TRANG (BẮT BUỘC TRÊN CÙNG)
# Chuyển layout sang "wide" để bảng hiển thị rộng rãi, dễ nhìn cho nhiều người
st.set_page_config(page_title="PHẦN MỀM TÍNH LƯƠNG HÀNG LOẠT", page_icon="💰", layout="wide")

# Kiểm tra và hiển thị Logo
if os.path.exists("LOGO.JPG"):
    st.image("LOGO.JPG")
elif os.path.exists("logo.jpg"):
    st.image("logo.jpg")

st.title("PHẦN MỀM TÍNH TIỀN LƯƠNG HÀNG LOẠT HV ĐẶNG NGỌC SANG")
st.markdown("Hỗ trợ tính toán nhanh gọn cho tối đa 500 người lao động. Bạn có thể thay đổi dữ liệu trực tiếp trên bảng hoặc copy/paste từ file Excel có sẵn.")
st.markdown("---")

# 2. CHỌN SỐ LƯỢNG NGƯỜI LAO ĐỘNG
col_input, _ = st.columns([1, 2])
with col_input:
    num_employees = st.number_input("Chọn số lượng nhân viên cần tính toán (Từ 1 - 500):", 
                                    min_value=1, max_value=500, value=5, step=1)

# 3. TẠO BẢNG NHẬP LIỆU (DATAFRAME)
# Khởi tạo dữ liệu mặc định dựa trên số lượng đã chọn
default_data = {
    "Mã NV": [f"NV{i:03d}" for i in range(1, num_employees + 1)],
    "Họ Tên": [f"Nhân viên {i}" for i in range(1, num_employees + 1)],
    "Lương CB (Tr)": [15.0] * num_employees,
    "Thưởng (Tr)": [2.0] * num_employees,
    "PC có BHXH (Tr)": [3.0] * num_employees,
    "PC không BHXH (Tr)": [1.0] * num_employees,
    "Số NPT (Người)": [1] * num_employees
}

df_input = pd.DataFrame(default_data)

st.markdown("### 📝 BẢNG NHẬP LIỆU ĐẦU VÀO")
st.caption("Mẹo: Chọn ô đầu tiên của bảng và nhấn Ctrl+V / Cmd+V để dán dữ liệu từ Excel vào.")

# Trình chỉnh sửa dữ liệu trên web
edited_df = st.data_editor(df_input, num_rows="dynamic", use_container_width=True)

# 4. XỬ LÝ LOGIC TÍNH TOÁN KHI BẤM NÚT
if st.button("TÍNH LƯƠNG HÀNG LOẠT", type="primary", use_container_width=True):
    # Tạo bản sao để chứa kết quả
    df_res = edited_df.copy()
    
    # Tính Tổng thu nhập và BHXH
    df_res["Tổng Thu Nhập"] = df_res["Lương CB (Tr)"] + df_res["Thưởng (Tr)"] + df_res["PC có BHXH (Tr)"] + df_res["PC không BHXH (Tr)"]
    df_res["Tiền Đóng BHXH"] = (df_res["Lương CB (Tr)"] + df_res["PC có BHXH (Tr)"]) * 0.105
    
    # Tính Thu nhập chịu thuế (Loại trừ phụ cấp không BHXH/miễn thuế)
    df_res["TN Chịu Thuế"] = df_res["Lương CB (Tr)"] + df_res["Thưởng (Tr)"] + df_res["PC có BHXH (Tr)"]
    
    # Tính Tổng giảm trừ và Thu nhập tính thuế (TNTT)
    df_res["Tổng Giảm Trừ"] = 15.5 + (6.2 * df_res["Số NPT (Người)"]) + df_res["Tiền Đóng BHXH"]
    df_res["TNTT"] = (df_res["TN Chịu Thuế"] - df_res["Tổng Giảm Trừ"]).clip(lower=0)
    
    # Hàm tính thuế lũy tiến 5 bậc
    def calc_tax(t):
        if t <= 0: return 0.0
        elif t <= 10: return t * 0.05
        elif t <= 30: return t * 0.1 - 0.5
        elif t <= 60: return t * 0.2 - 3.5
        elif t <= 100: return t * 0.3 - 9.5
        else: return t * 0.35 - 14.5
        
    df_res["Thuế TNCN"] = df_res["TNTT"].apply(calc_tax)
    
    # Tính Thực lãnh
    df_res["Thực Lãnh"] = df_res["Tổng Thu Nhập"] - df_res["Tiền Đóng BHXH"] - df_res["Thuế TNCN"]
    
    # Làm tròn 2 chữ số thập phân cho gọn gàng
    cols_to_round = ["Tổng Thu Nhập", "Tiền Đóng BHXH", "TN Chịu Thuế", "Tổng Giảm Trừ", "TNTT", "Thuế TNCN", "Thực Lãnh"]
    df_res[cols_to_round] = df_res[cols_to_round].round(2)

    # 5. HIỂN THỊ KẾT QUẢ
    st.markdown("---")
    st.markdown("### 📊 BẢNG KẾT QUẢ TÍNH TOÁN CHI TIẾT")
    st.dataframe(df_res, use_container_width=True)
    
    # 6. TỔNG HỢP CHI PHÍ TOÀN CÔNG TY
    st.markdown("### 📈 TỔNG HỢP CHI PHÍ TOÀN DOANH NGHIỆP")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tổng Quỹ Lương (Gross)", f"{df_res['Tổng Thu Nhập'].sum():,.2f} Tr")
    m2.metric("Tổng BHXH Đã Trích", f"{df_res['Tiền Đóng BHXH'].sum():,.2f} Tr")
    m3.metric("Tổng Nộp Thuế TNCN", f"{df_res['Thuế TNCN'].sum():,.2f} Tr")
    m4.metric("Tổng Tiền Thực Lãnh (Net)", f"{df_res['Thực Lãnh'].sum():,.2f} Tr")
    
    # 7. XUẤT FILE EXCEL
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_res.to_excel(writer, index=False, sheet_name='Bang_Luong_Ket_Qua')
    excel_data = output.getvalue()
    
    st.download_button(
        label="📥 TẢI XUỐNG FILE EXCEL TỔNG HỢP (.xlsx)",
        data=excel_data,
        file_name="Bang_Tinh_Luong_Tong_Hop.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="secondary"
    )
