import math
import calculator_pb2
import calculator_pb2_grpc

class calculatorLogic(calculator_pb2.CalculatorServicer):
    def Calculate(self, request, context):
        operation = request.operation
        operands = list(request.operands)

        result, error_message = self._excute(operation, operands)

        has_error = error_message != ""

        return calculator_pb2_grpc.CalculateResponse(reuslt=result, has_error=has_error, error_message=error_message)
    
    def _excute(self, operation, operands):
        op = operation.lower()

        #nhóm 2 toán hạng
        if op in ["add", "+", "subtract", "-", "multiply", "*", "divide", "/", "power", "^", "modulo", "%"]:
            if len(operands) < 2:
                return 0, "Lỗi phép tính yêu cầu ít nhất 2 toán hạng"
            
            a = operands[0]
            b = operands[1]

            if op in ["add", "+"]:
                return a + b, ""
            elif op in ["subtract", "-"]:
                return a - b, ""
            elif op in ["multiply", "*"]:
                return a * b, ""
            elif op in ["divide", "/"]:
                if b == 0:
                    return 0.0, "Lỗi!!! không thể chia cho 0"
                return a / b, ""
            elif op in ['power', '^']:
                return math.pow(a,b), ""
            elif op in ["modulo", "%"]:
                if b == 0:
                    return 0.0, "Lỗi!!! không thể chia lấy dư cho 0"
                return a % b, ""
            
        #nhóm 1 toán hạng
        elif op in ["sqrt", "square", "sin", "cos", "tan", "log", "ln", "factorial", "!", "negate", "abs"]:
            a = operands[0]
            if op == "sqrt":
                if a < 0:
                    return 0, "Lỗi!!! Không thể tính căn bậc 2 cho số âm"
                return math.sqrt(a), ""
            elif op == "square":
                return a * a, ""
            elif op == "sin":
                return math.sin(math.radians(a)), ""
            elif op == "cos":
                return math.cos(math.radians(a)), ""
            elif op == "tan":
                if a % 180 == 90:
                    return 0, "Lỗi!!! Không thể tính tan của gốc này"
                return math.tan(math.radians(a)), ""
            elif op == "log":
                if a <= 0:
                    return 0, "Lỗi!!! Biểu thức dưới dấu log (log10) phải > 0"
                return math.log10(a), ""
            elif op == "ln":
                if a <= 0:
                    return 0, "Lỗi!!! Biểu thức dưới dấu ln phải > 0"
                return math.log(a), ""
            elif op in ["factorial", "!"]:
                if a < 0 or a >= 170 or not a.is_integer():
                    return 0, "Lỗi!!! Không thể tính giai thừa"
                return float(math.factorial(int(a))), ""
            elif op == "negate":
                return -a, ""
            elif op == "abs":
                return abs(a), ""
            
        else:
            return 0, "Lỗi!!! phép tính này không được hỗ trợ"