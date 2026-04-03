import grpc
import calculator_pb2
import calculator_pb2_grpc

class CalculatorClient:
    def __init__(self):
        server_ip = self._ask_server_ip()

        target = f"{server_ip}:50051"
        self.channel = grpc.insecure_channel(target)

        self.stub = calculator_pb2_grpc.CalculatorStub(self.channel)

    def _ask_server_ip(self):
        ip = input("Nhập IP Server (để trống sẽ chọn localhost): ")
        return ip.strip() if ip.strip() else "localhost"

    def _call(self, operation: str, operands: list[float]):
        try:
            request = calculator_pb2.CalculateRequest(
                operation=operation,
                operands=operands,
            )
            response = self.stub.Calculate(request)

            if response.has_error:
                return None, response.error_message
            return response.result, None

        except grpc.RpcError as e:
            return None, f"Lỗi kết nối: {e.details()}"

    def _call_server(self, expr: str):
        """Gửi biểu thức thô (string) lên server – dùng cho proto expression."""
        try:
            request = calculator_pb2.CalculateRequest(expression=expr)
            response = self.stub.Calculate(request)
            return response
        except grpc.RpcError as e:
            print(f"Lỗi kết nối gRPC hoặc Server ngắt kết nối: {e.details()}")
            return None

    def _ping_server(self):
        try:
            req = calculator_pb2.CalculateRequest(
                operation="add",
                operands=[1.0, 1.0],
            )
            resp = self.stub.Calculate(req)

            if not resp.has_error:
                print("Trạng thái: Đã kết nối và sẵn sàng")
                return True
            else:
                print(f"Trạng thái: Server phản hồi lỗi - {resp.error_message}")
                return False

        except grpc.RpcError:
            print("Trạng thái: Không kết nối được server (Timeout/Offline)")
            return False
    def _on_close(self):
        if self.channel is not None:
            self.channel.close()