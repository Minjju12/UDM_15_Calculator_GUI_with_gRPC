import tkinter as tk
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

if __name__ == "__main__":
    root = tk.Tk()
    Calculator(root)
    root.mainloop()
