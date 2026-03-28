import grpc
import calculator_pb2
import calculator_pb2_grpc

class CalculatorClient:
    def __init__(self):
        # Thực hiện hỏi địa chỉ IP Server 
        ip_address = self._ask_server_ip()
        
        # Thiết lập kênh truyền tới cổng 50051 
        target = f"{ip_address}:50051"
        self.channel = grpc.insecure_channel(target)
        
        # Tạo đối tượng stub để gọi hàm từ xa 
        self.stub = calculator_pb2_grpc.CalculatorStub(self.channel)

    def _ask_server_ip(self):
        ip = input("Nhập IP Server (để trống sẽ chọn localhost): ")
        return ip if ip.strip() else "localhost"

    def _call(self, operation: str, operands: list):
        # Truyền và nhận thông tin
        try:
            request = calculator_pb2.CalculateRequest(
                operation=operation,
                operands=operands
            )
            response = self.stub.Calculate(request)
            return response
            
        except grpc.RpcError as e:
            print(f"Lỗi kết nối gRPC: {e.details()}")
            return None

    def _ping_server(self):
        try:        
            grpc.channel_ready_future(self.channel).result(timeout=2)
            print("Trạng thái: Đã kết nối") 
            return True
        except grpc.FutureTimeoutError:
            print("Trạng thái: Lỗi") 
            return False

    def _on_close(self):
        if self.channel is not None:
            self.channel.close()