import tkinter as tk
import re
import grpc

import calculator_pb2
import calculator_pb2_grpc
#bảng màu
BG      = "#1e1e1e"
BTN_NUM = "#2e2e2e"
BTN_OP  = "#3a3a3a"
BTN_SCI = "#2a2a2a"
BTN_CLR = "#3a3a3a"
BTN_DEL = "#3a3a3a"
BTN_EQ  = "#00bcd4"
BTN_PAR = "#3a3a3a"
FG      = "white"
#thêm giói hạn số vd 15 lần số 9 ,k được nhập nhiều
MAX_CONSECUTIVE_DIGITS = 15

def fmt(val: float) -> str:
    """Định dạng số để hiển thị."""
    if math.isnan(val):  return "NaN"
    if math.isinf(val):  return "∞" if val > 0 else "-∞"
    if abs(val) >= 1e15 or (abs(val) < 1e-9 and val != 0):
        return f"{val:.6e}"
    if val == int(val) and abs(val) < 1e15:
        return str(int(val))
    return f"{val:.10g}"

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.expression = ""        
        self.result_shown = False

        self._build_display()
        self._build_buttons()
        #self._ping_server()
        
#=========================
# def ask_server_ip
#========================

#=======================
#giao dien
#=====================
    def _build_display(self):
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(fill="x", padx=14, pady=(14, 4))

        # Dòng nhỏ: hiển thị biểu thức đang nhập
        self.expr_var = tk.StringVar(value="")
        tk.Label(frame, textvariable=self.expr_var,
                 font=("Segoe UI", 11), bg=BG, fg="#aaaaaa",
                 anchor="e", wraplength=340, justify="right").pack(fill="x")

        # Dòng lớn: hiển thị kết quả hoặc số đang nhập
        self.main_var  = tk.StringVar(value="0")
        self.main_lbl  = tk.Label(frame, textvariable=self.main_var,
                                  font=("Segoe UI", 34, "bold"), bg=BG, fg="white",
                                  anchor="e")
        self.main_lbl.pack(fill="x")

        # Dòng trạng thái kết nối
        self.status_var = tk.StringVar(value="Đang kết nối...")
        tk.Label(frame, textvariable=self.status_var,
                 font=("Segoe UI", 9), bg=BG, fg="#4ade80",
                 anchor="e").pack(fill="x")

        tk.Frame(self.root, bg="#3c3c3c", height=1).pack(fill="x", padx=14)

    #nút
    def _build_buttons(self):
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(padx=14, pady=14)

        for col in range(5):
            frame.columnconfigure(col, weight=1, minsize=64)
        for row in range(8):
            frame.rowconfigure(row, weight=1, minsize=52)

        layout = [
            # Hàng 0: sin, cos, tan, log, ln
            ("sin",  0, 0, BTN_SCI, 1, 1), ("cos",  0, 1, BTN_SCI, 1, 1),
            ("tan",  0, 2, BTN_SCI, 1, 1), ("log",  0, 3, BTN_SCI, 1, 1),
            ("ln",   0, 4, BTN_SCI, 1, 1),
            # Hàng 1: x², xʸ, √, ∛, π
            ("x²",   1, 0, BTN_SCI, 1, 1), ("xʸ",   1, 1, BTN_SCI, 1, 1),
            ("√",    1, 2, BTN_SCI, 1, 1), ("∛",    1, 3, BTN_SCI, 1, 1),
            ("π",    1, 4, BTN_SCI, 1, 1),

            ("e",    2, 0, BTN_SCI, 1, 1), ("n!",   2, 1, BTN_SCI, 1, 1),
            ("±",    2, 2, BTN_SCI, 1, 1), ("%",    2, 3, BTN_SCI, 1, 1),
            ("abs(",    2, 4, BTN_SCI, 1, 1),
            # Hàng 3: ), abs(, mod, C, ⌫
            ("mod",    3, 0, BTN_SCI, 1, 1), ("(", 3, 1, BTN_PAR, 1, 1),
            (")",  3, 2, BTN_PAR, 1, 1), ("C",    3, 3, BTN_CLR, 1, 1),
            ("⌫",    3, 4, BTN_DEL, 1, 1),
            # Hàng 4-7:số-dấu 
            ("7",    4, 0, BTN_NUM, 1, 1), ("8",    4, 1, BTN_NUM, 1, 1),
            ("9",    4, 2, BTN_NUM, 1, 1), ("÷",    4, 3, BTN_OP,  1, 2),
            ("4",    5, 0, BTN_NUM, 1, 1), ("5",    5, 1, BTN_NUM, 1, 1),
            ("6",    5, 2, BTN_NUM, 1, 1), ("×",    5, 3, BTN_OP,  1, 2),
            ("1",    6, 0, BTN_NUM, 1, 1), ("2",    6, 1, BTN_NUM, 1, 1),
            ("3",    6, 2, BTN_NUM, 1, 1), ("-",    6, 3, BTN_OP,  1, 1),
            ("=",    6, 4, BTN_EQ,  2, 1),
            ("0",    7, 0, BTN_NUM, 1, 2), (".",    7, 2, BTN_NUM, 1, 1),
            ("+",    7, 3, BTN_OP,  1, 1),
        ]
        
        for (text, row, col, color, rs, cs) in layout:
            btn = tk.Button(
                frame, text=text, bg=color, fg=FG,
                font=("Segoe UI", 12, "bold"),
                relief="flat", bd=0,
                activebackground="#484848", activeforeground="white",
                cursor="hand2",
                command=lambda t=text: self._on_click(t),
            )
            btn.grid(row=row, column=col, rowspan=rs, columnspan=cs,
                     padx=3, pady=3, sticky="nsew")
    
    # ===============
    # Hiển thị
    # =================

    def _refresh_display(self):
        #Cập nhật màn hình chính và tự động thu nhỏ font nếu chuỗi dài
        text = self.expression if self.expression else "0"
        self.main_var.set(text)

        #giảm dần theo độ dài
        length = len(text)
        if   length <= 8:   size = 34
        elif length <= 12:  size = 28
        elif length <= 18:  size = 22
        elif length <= 24:  size = 17
        else:               size = 13

        self.main_lbl.configure(font=("Segoe UI", size, "bold"))

    def _consecutive_digits_at_end(self) -> int:
        #Đếm số chữ số liên tiếp ở cuối chuỗi biểu thức.
        count = 0
        for ch in reversed(self.expression):
            if ch.isdigit() or ch == ".":
                count += 1
            else:
                break
        return count

    def _can_append_digit(self) -> bool:
        return self._consecutive_digits_at_end() < MAX_CONSECUTIVE_DIGITS
    
    #====================
    #grpc(ping server,call_server)
    #==================

    #===================
    #on_click
    #==================

    def _on_click(self, key: str):

        # C: Xóa sạch
        if key == "C":
            self.expression   = ""
            self.result_shown = False
            self.expr_var.set("")
            self._refresh_display()
            return

        # ⌫: Xóa 1 ký tự 
        if key == "⌫":
            if self.result_shown:
                # Sau khi có kết quả, ⌫ xóa toàn bộ (giống iOS)
                self.expression   = ""
                self.result_shown = False
            else:
                self.expression = self.expression[:-1]
            self.expr_var.set("")
            self._refresh_display()
            return

        # = : Gửi lên server 
        if key == "=":
            expr = self.expression.strip()
            if not expr:
                return
            # Tự đóng ngoặc còn thiếu
            open_count = expr.count("(") - expr.count(")")
            expr += ")" * max(open_count, 0)

            self.expr_var.set(expr + "  =")
            result, err = self._call_server(expr)

            if err:
                self.expression   = ""
                self.result_shown = False
                self.main_var.set("Lỗi")
                self.main_lbl.configure(font=("Segoe UI", 34, "bold"))
                self.expr_var.set(err)
            else:
                self.expression   = result
                self.result_shown = True
                self._refresh_display()
            return

        # Nếu vừa hiển thị kết quả 
        # Bấm số/dấu chấm → bắt đầu biểu thức mới
        # Bấm toán tử     → dùng kết quả làm toán hạng đầu
        if self.result_shown:
            if key.isdigit() or key == ".":
                self.expression   = ""
                self.result_shown = False
            elif key not in ("π", "e") and not key.endswith("("):
                # Toán tử nhị phân, giữ kết quả làm vế trái
                self.result_shown = False
            else:
                # Hàm/hằng số sau kết quả → nhân ẩn rồi tiếp tục
                self.expression  += "×"
                self.result_shown = False

        # Chữ số & dấu chấm 
        if key.isdigit():
            if not self._can_append_digit():
                return   # Input Guard: vượt quá giới hạn
            # Xoá số 0 đứng đầu đơn lẻ
            if self.expression.endswith("0") and not self.expression[:-1].endswith((".", *"0123456789")):
                self.expression = self.expression[:-1]
            self.expression += key
            self._refresh_display()
            return

        if key == ".":
            # Tránh 2 dấu chấm trong cùng 1 số
            # Lấy phần số cuối (sau toán tử / dấu mở ngoặc cuối cùng)
            last_num_match = re.search(r'[\d.]+$', self.expression)
            if last_num_match and "." in last_num_match.group():
                return
            if not self.expression or not self.expression[-1].isdigit():
                self.expression += "0"
            self.expression += "."
            self._refresh_display()
            return

        # Hằng số 
        if key in ("π", "e"):
            # Nhân ẩn nếu trước đó là số hoặc đóng ngoặc
            if self.expression and (self.expression[-1].isdigit() or self.expression[-1] in (")", "π", "e")):
                self.expression += "×"
            self.expression += key
            self._refresh_display()
            return

        # Hàm 1 ngôi → in prefix dạng "func(" 
        # Khi bấm sin, cos, tan, log, ln, √, n!, abs(  → chèn chuỗi mở ngoặc
        FUNC_MAP = {
            "sin":  "sin(",
            "cos":  "cos(",
            "tan":  "tan(",
            "log":  "log(",
            "ln":   "ln(",
            "√":    "sqrt(",
            "abs(": "abs(",
        }
        if key in FUNC_MAP:
            # Nhân ẩn nếu số / đóng ngoặc đứng trước
            if self.expression and (self.expression[-1].isdigit() or self.expression[-1] in (")", "π", "e")):
                self.expression += "×"
            self.expression += FUNC_MAP[key]
            self._refresh_display()
            return

        # n! → hậu tố "!" 
        if key == "n!":
            if self.expression and (self.expression[-1].isdigit() or self.expression[-1] == ")"):
                self.expression += "!"
                self._refresh_display()
            return

        # x² → hậu tố "²" 
        if key == "x²":
            if self.expression and (self.expression[-1].isdigit() or self.expression[-1] in (")", "π", "e")):
                self.expression += "²"
                self._refresh_display()
            return

        # xʸ → toán tử lũy thừa "^" 
        if key == "xʸ":
            if self.expression and (self.expression[-1].isdigit() or self.expression[-1] in (")", "π", "e")):
                self.expression += "^"
                self._refresh_display()
            return

         # ± : đổi dấu biểu thức hiện tại 
        if key == "±":
            if not self.expression:
                self.expression = "-"
            elif self.expression.startswith("-"):
                self.expression = self.expression[1:]
            else:
                self.expression = "-(" + self.expression + ")"
            self._refresh_display()
            return

        # % : thêm /100
        if key == "%":
            if self.expression:
                self.expression += "/100"
                self._refresh_display()
            return

        #mod
        if key == "mod":
            if self.expression:
                self.expression += " mod "
                self._refresh_display()
            return        




if __name__ == "__main__":
    root = tk.Tk()
    Calculator(root)
    root.mainloop()
