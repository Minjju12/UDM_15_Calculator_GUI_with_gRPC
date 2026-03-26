import grpc
from concurrent import futures

import calculator_pb2_grpc

# import class logic của bạn (file loginserve)
from loginserve import calculatorLogic


def serve():
    # 1. Khởi tạo server với đa luồng
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # 2. Sử dụng lại service từ proto (add_CalculatorServicer_to_server)
    calculator_pb2_grpc.add_CalculatorServicer_to_server(
        calculatorLogic(), server
    )

    # 3. Mở cổng 50051 (insecure)
    server.add_insecure_port('[::]:50051')

    # 4. Khởi động server
    server.start()
    print("🚀 Server đang chạy tại port 50051...")

    try:
        # 5. Giữ server chạy
        server.wait_for_termination()

    except KeyboardInterrupt:
        # 6. Xử lý Ctrl + C (Graceful stop)
        print("\n🛑 Đang tắt server...")
        server.stop(0)
        print("✅ Server đã tắt an toàn")


if __name__ == '__main__':
    serve()