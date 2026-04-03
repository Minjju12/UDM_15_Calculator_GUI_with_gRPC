import grpc
import math
from concurrent import futures
import calculator_pb2
import calculator_pb2_grpc

class CalculatorServicer(calculator_pb2_grpc.CalculatorServicer):
    SAFE_MATH_ENV = {
        "__builtins__": {},
        "int":      int,
        "math": math,
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
        "pi":       math.pi,
        "e":        math.e,
    }

    def Calculate(self, request, context):
        raw = request.expression.strip()
        try:
            result = self._safe_eval(raw)
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
                parens = 1
                left -= 1
                while left >= 0 and parens > 0:
                    if expr[left] == ")": parens += 1
                    elif expr[left] == "(": parens -= 1
                    left -= 1
                start = left + 1
            else:
                while left >= 0 and (expr[left].isdigit() or expr[left] == '.'):
                    left -= 1
                start = left + 1
            operand = expr[start:idx]
            expr = expr[:start] + f"factorial(int({operand}))" + expr[idx+1:]

        result = eval(expr, self.SAFE_MATH_ENV)     
        return float(result)
