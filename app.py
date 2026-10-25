import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf

# --- CÁC HÀM CORE LOGIC XỬ LÝ TÍNH TOÁN ---
def calculate_npv(rate, cash_flows):
    """Tính Giá trị hiện tại ròng (NPV)"""
    return npf.npv(rate, cash_flows)

def calculate_irr(cash_flows):
    """Tính Tỷ suất sinh lời nội bộ (IRR)"""
    try:
        return npf.irr(cash_flows)
    except:
        return None

def calculate_mirr(rate, cash_flows):
    """Tính Tỷ suất sinh lời nội bộ có điều chỉnh (MIRR)"""
    return npf.mirr(cash_flows, finance_rate=rate, reinvest_rate=rate)

def calculate_pi(rate, cash_flows):
    """Tính Chỉ số lợi nhuận (PI)"""
    pv_outflows = sum(cf / (1 + rate)**i for i, cf in enumerate(cash_flows) if cf < 0)
    pv_inflows = sum(cf / (1 + rate)**i for i, cf in enumerate(cash_flows) if cf > 0)
    if pv_outflows == 0:
        return 0
    return pv_inflows / abs(pv_outflows)

def calculate_pp(cash_flows):
    """Tính Thời gian hoàn vốn không chiết khấu (PP)"""
    cumulative_cf = np.cumsum(cash_flows)
    for i in range(len(cumulative_cf) - 1):
        if cumulative_cf[i] < 0 and cumulative_cf[i+1] >= 0:
            # Áp dụng công thức nội suy tìm số tháng
            return i + abs(cumulative_cf[i]) / cash_flows[i+1]
    return -1 # Không hoàn vốn

def calculate_dpp(rate, cash_flows):
    """Tính Thời gian hoàn vốn có chiết khấu (DPP)"""
    discounted_cfs = [cf / (1 + rate)**i for i, cf in enumerate(cash_flows)]
    cumulative_dcf = np.cumsum(discounted_cfs)
    for i in range(len(cumulative_dcf) - 1):
        if cumulative_dcf[i] < 0 and cumulative_dcf[i+1] >= 0:
             # Áp dụng công thức nội suy tìm số tháng
            return i + abs(cumulative_dcf[i]) / discounted_cfs[i+1]
    return -1 # Không hoàn vốn

# --- XÂY DỰNG GIAO DIỆN APP (UI) ---
st.set_page_config(page_title="App Thẩm Định Tài Chính Dự Án", layout="wide")

st.title("📊 Ứng dụng Thẩm định Tài chính Dự án Đầu tư")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Nhập liệu")
    initial_investment = st.number_input(
        "Vốn đầu tư ban đầu (Tỷ đồng - Nhập số dương, phần mềm sẽ tự hiểu là dòng tiền âm năm 0):", 
        min_value=0.0, value=1000.0, step=10.0
    )
    discount_rate_percent = st.number_input(
        "Lãi suất chiết khấu (%):", 
        min_value=0.0, max_value=100.0, value=20.0, step=1.0
    )
    project_years = st.number_input(
        "Số năm của dự án (Không tính năm 0):", 
        min_value=1, max_value=50, value=5, step=1
    )
    
    discount_rate = discount_rate_percent / 100.0
    
    st.subheader("Dòng tiền các năm (Tỷ đồng)")
    cash_flows_input = []
    # Tự động render số ô nhập liệu tương ứng với số năm dự án
    for i in range(1, project_years + 1):
        cf = st.number_input(f"Dòng tiền Năm {i}:", value=0.0, step=10.0, key=f"cf_{i}")
        cash_flows_input.append(cf)
        
    calculate_btn = st.button("Tính toán các chỉ số", type="primary")

with col2:
    st.header("Kết quả tính toán")
    if calculate_btn:
        # Gom vốn đầu tư năm 0 và dòng tiền các năm thành 1 mảng
        cash_flows = [-initial_investment] + cash_flows_input
        
        # Bảng hiển thị thông số dòng tiền
        df_cf = pd.DataFrame({"Năm": range(project_years + 1), "Dòng tiền (Tỷ đồng)": cash_flows})
        st.write("**Bảng dòng tiền dự án:**")
        st.dataframe(df_cf.set_index("Năm").T, use_container_width=True)
        
        st.markdown("### Các chỉ số tài chính")
        
        # Chạy logic tính toán
        npv = calculate_npv(discount_rate, cash_flows)
        irr = calculate_irr(cash_flows)
        mirr = calculate_mirr(discount_rate, cash_flows)
        pi = calculate_pi(discount_rate, cash_flows)
        pp = calculate_pp(cash_flows)
        dpp = calculate_dpp(discount_rate, cash_flows)
        
        # Render kết quả ra màn hình Dashboard
        c1, c2, c3 = st.columns(3)
        c1.metric(label="Giá trị hiện tại ròng (NPV)", value=f"{npv:,.2f} Tỷ", delta="Khả thi" if npv > 0 else "Không khả thi")
        
        if irr is not None:
            c2.metric(label="Tỷ suất sinh lời nội bộ (IRR)", value=f"{irr*100:,.2f} %", delta="Lớn hơn chiết khấu" if irr > discount_rate else "Nhỏ hơn chiết khấu")
        else:
             c2.metric(label="Tỷ suất sinh lời nội bộ (IRR)", value="Không xác định")
             
        c3.metric(label="Chỉ số lợi nhuận (PI)", value=f"{pi:,.3f}", delta="> 1 (Tốt)" if pi > 1 else "< 1 (Kém)")
        
        c4, c5, c6 = st.columns(3)
        if not np.isnan(mirr):
             c4.metric(label="IRR có điều chỉnh (MIRR)", value=f"{mirr*100:,.2f} %")
        else:
             c4.metric(label="IRR có điều chỉnh (MIRR)", value="N/A")
             
        c5.metric(label="Thời gian hoàn vốn (PP)", value=f"{pp:,.2f} năm" if pp != -1 else "Không hoàn vốn")
        c6.metric(label="Thời gian hoàn vốn có chiết khấu (DPP)", value=f"{dpp:,.2f} năm" if dpp != -1 else "Không hoàn vốn")
        
        # Khối Kết luận tự động
        st.markdown("### Kết luận chung")
        if npv > 0 and (irr is not None and irr > discount_rate):
            st.success(f"**DỰ ÁN KHẢ THI:** NPV dương ({npv:,.2f} tỷ đồng) và IRR ({irr*100:,.2f}%) lớn hơn mức lãi suất chiết khấu ({discount_rate_percent}%).")
        else:
            st.error(f"**DỰ ÁN KHÔNG KHẢ THI:** NPV âm ({npv:,.2f} tỷ đồng) hoặc IRR ({irr*100:,.2f}%) nhỏ hơn mức lãi suất chiết khấu ({discount_rate_percent}%).")
