import grpc
import math
from concurrent import futures
import calculator_pb2
import calculator_pb2_grpc

class CalculatorServicer(calculator_pb2_grpc.CalculatorServicer):
    # Nhận chuỗi biểu thức từ client, phân tích và tính toán bằng eval()
    # Các hàm toán học được phép dùng trong eval()
    SAFE_MATH_ENV = {
        "__builtins__": {},
        "int":      int,
        "math": math,
        # Hàm thông dụng
        "sin":      math.sin,
        "cos":      math.cos,
        "tan":      math.tan,
        "log":      math.log10,
        "ln":       math.log,
        "sqrt":     math.sqrt,
        "cbrt":     math.cbrt,
        "factorial": math.factorial,
        "abs":      abs,
        "pow":      math.pow,
        # Hằng số
        "pi":       math.pi,
        "e":        math.e,
    }

    def Calculate(self, request, context):
        raw = request.expression.strip()
        print(f"[SERVER] expression={raw!r}")

        try:
            result = self._safe_eval(raw)

            # Kiểm tra kết quả hợp lệ
            if math.isnan(result):
                return calculator_pb2.CalculateResponse(has_error=True, error_message="Kết quả không xác định (NaN)")
            if math.isinf(result):
                sign = "∞" if result > 0 else "-∞"
                return calculator_pb2.CalculateResponse(has_error=True, error_message=f"Kết quả vô cực ({sign})")

            return calculator_pb2.CalculateResponse(result=result, has_error=False)

        except ZeroDivisionError:
            return calculator_pb2.CalculateResponse(has_error=True, error_message="Không thể chia cho 0")
        except ValueError as e:
            return calculator_pb2.CalculateResponse(has_error=True, error_message=str(e))
        except SyntaxError:
            return calculator_pb2.CalculateResponse(has_error=True, error_message="Biểu thức không hợp lệ")
        except Exception as e:
            return calculator_pb2.CalculateResponse(has_error=True, error_message=f"Lỗi: {e}")

    def _safe_eval(self, expr: str) -> float:
        # Dịch ký hiệu giao diện sang Python hợp lệ 
        expr = expr.replace("π", "pi")          
        expr = expr.replace("×", "*")          
        expr = expr.replace("÷", "/")          
        expr = expr.replace("mod", "%")         
        expr = expr.replace("^", "**")          
        expr = expr.replace("²", "**2")         

        while "!" in expr:
            idx = expr.find("!")
            left = idx - 1
            if expr[left] == ")":
                # Quét lùi để tìm dấu ngoặc mở '(' tương ứng
                parens = 1
                left -= 1
                while left >= 0 and parens > 0:
                    if expr[left] == ")": parens += 1
                    elif expr[left] == "(": parens -= 1
                    left -= 1
                start = left + 1
            else:
                # Quét lùi để tìm điểm bắt đầu của con số
                while left >= 0 and (expr[left].isdigit() or expr[left] == '.'):
                    left -= 1
                start = left + 1
            
            # Tách biểu thức cần tính giai thừa và thay thế vào chuỗi
            operand = expr[start:idx]
            expr = expr[:start] + f"factorial(int({operand}))" + expr[idx+1:]

        print(f"[SERVER] parsed  ={expr!r}")
        result = eval(expr, self.SAFE_MATH_ENV)   
        return float(result)

#khởi động server
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calculator_pb2_grpc.add_CalculatorServicer_to_server(CalculatorServicer(), server)

    port = server.add_insecure_port("[::]:50051")
    server.start()
    print("Server đang chạy... (Ctrl+C để dừng)\n")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n[SERVER] Đã dừng.")
        server.stop(0)


if __name__ == "__main__":
    serve()
