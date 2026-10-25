class ProjectAppraisalApp:
    def __init__(self, initial_investment, discount_rate, project_years, annual_cash_flows):
        """
        Khởi tạo đối tượng tính toán các chỉ số dự án.
        
        :param initial_investment: Vốn đầu tư ban đầu (Tỷ đồng). Luôn là số dương (code sẽ tự động chuyển thành số âm).
        :param discount_rate: Lãi suất chiết khấu (dạng số thập phân, VD: 20% = 0.20)
        :param project_years: Số năm hoạt động của dự án (Tương ứng với số lượng dòng tiền các năm).
        :param annual_cash_flows: Mảng chứa dòng tiền thuần các năm (từ năm 1 đến năm n).
        """
        self.r = discount_rate
        self.n = project_years
        
        # Kiểm tra tính hợp lệ của dữ liệu đầu vào
        if len(annual_cash_flows) != self.n:
            raise ValueError(f"Lỗi: Số lượng dòng tiền ({len(annual_cash_flows)}) không khớp với số năm dự án ({self.n}).")
            
        # Ghép vốn đầu tư (năm 0, mang dấu âm) với dòng tiền các năm
        self.cfs = [-abs(initial_investment)] + annual_cash_flows

    def calculate_npv(self):
        """1. Tính Giá trị hiện tại ròng (NPV) - Đơn vị: Tỷ đồng"""
        npv = sum(cf / (1 + self.r)**t for t, cf in enumerate(self.cfs))
        return npv

    def calculate_irr(self, iterations=1000, tolerance=1e-6):
        """2. Tính Tỷ suất sinh lời nội bộ (IRR) bằng phương pháp nội suy"""
        low, high = -0.99, 2.0 # Giới hạn tìm kiếm từ -99% đến 200%
        for _ in range(iterations):
            mid = (low + high) / 2
            current_npv = sum(cf / (1 + mid)**t for t, cf in enumerate(self.cfs))
            
            if abs(current_npv) < tolerance:
                return mid
            
            if current_npv > 0:
                low = mid
            else:
                high = mid
        return mid

    def calculate_mirr(self):
        """3. Tính Tỷ suất sinh lời nội bộ có điều chỉnh (MIRR)"""
        # PV của dòng tiền âm (Quy về năm 0)
        pv_outflows = sum(cf / (1 + self.r)**t for t, cf in enumerate(self.cfs) if cf < 0)
        # FV của dòng tiền dương (Quy về năm cuối cùng n)
        fv_inflows = sum(cf * (1 + self.r)**(self.n - t) for t, cf in enumerate(self.cfs) if cf > 0)
        
        if pv_outflows == 0:
            return 0
            
        mirr = (fv_inflows / abs(pv_outflows))**(1 / self.n) - 1
        return mirr

    def calculate_pi(self):
        """4. Tính Chỉ số lợi nhuận (PI)"""
        pv_outflows = sum(cf / (1 + self.r)**t for t, cf in enumerate(self.cfs) if cf < 0)
        pv_inflows = sum(cf / (1 + self.r)**t for t, cf in enumerate(self.cfs) if cf > 0)
        
        if pv_outflows == 0:
            return 0
            
        return pv_inflows / abs(pv_outflows)

    def calculate_pp(self):
        """5. Tính Thời gian hoàn vốn không chiết khấu (PP) - Đơn vị: Năm"""
        cumulative = 0
        for t, cf in enumerate(self.cfs):
            cumulative += cf
            if cumulative >= 0:
                if t == 0: return 0
                # Tính phần năm lẻ
                prev_cumulative = cumulative - cf
                return (t - 1) + abs(prev_cumulative) / cf
        return -1 # Không hòa vốn

    def calculate_dpp(self):
        """6. Tính Thời gian hoàn vốn có chiết khấu (DPP) - Đơn vị: Năm"""
        cumulative = 0
        for t, cf in enumerate(self.cfs):
            discounted_cf = cf / (1 + self.r)**t
            cumulative += discounted_cf
            if cumulative >= 0:
                if t == 0: return 0
                # Tính phần năm lẻ
                prev_cumulative = cumulative - discounted_cf
                return (t - 1) + abs(prev_cumulative) / discounted_cf
        return -1 # Không hòa vốn

    def get_results(self):
        """Hàm xuất toàn bộ kết quả dưới dạng Dictionary (thích hợp làm API trả về JSON)"""
        pp = self.calculate_pp()
        dpp = self.calculate_dpp()
        
        return {
            "NPV": round(self.calculate_npv(), 2),
            "IRR": round(self.calculate_irr() * 100, 2),    # Đổi ra %
            "MIRR": round(self.calculate_mirr() * 100, 2),  # Đổi ra %
            "PI": round(self.calculate_pi(), 4),
            "PP": round(pp, 2) if pp != -1 else "Không hoàn vốn",
            "DPP": round(dpp, 2) if dpp != -1 else "Không hoàn vốn"
        }

# ================= CÁCH GỌI VÀ SỬ DỤNG TRONG APP =================
if __name__ == "__main__":
    try:
        # Lấy dữ liệu giả định từ Form nhập liệu của App
        input_data = {
            "initial_investment": 1000,           # Vốn đầu tư (tự động nhận dấu âm trong code)
            "discount_rate": 0.20,                # Lãi suất chiết khấu 20%
            "project_years": 5,                   # Số năm dự án
            "annual_cash_flows": [500, -100, 400, 1000, 1800] # Dòng tiền từ năm 1 đến 5
        }
        
        # Khởi tạo thuật toán
        app = ProjectAppraisalApp(**input_data)
        
        # Trả kết quả tính toán
        results = app.get_results()
        
        # In ra màn hình console (hoặc trả về Frontend)
        print("--- KẾT QUẢ THẨM ĐỊNH DỰ ÁN ---")
        print(f"1. Giá trị hiện tại ròng (NPV) : {results['NPV']} (Tỷ đồng)")
        print(f"2. Tỷ suất sinh lời nội bộ (IRR) : {results['IRR']} %")
        print(f"3. Tỷ suất sinh lời nội bộ có điều chỉnh (MIRR) : {results['MIRR']} %")
        print(f"4. Chỉ số lợi nhuận (PI) : {results['PI']}")
        print(f"5. Thời gian hoàn vốn không chiết khấu (PP) : {results['PP']} năm")
        print(f"6. Thời gian hoàn vốn có chiết khấu (DPP) : {results['DPP']} năm")
        
    except ValueError as e:
        print(e)
