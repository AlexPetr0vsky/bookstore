import os
import grpc
import inventory_pb2
import inventory_pb2_grpc


class InventoryClient:
    def __init__(self, host: str = None, port: int = None):
        host = host or os.getenv("INVENTORY_HOST", "localhost")
        port = port or int(os.getenv("INVENTORY_PORT", 50051))
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = inventory_pb2_grpc.InventoryServiceStub(self.channel)

    def get_stock(self, book_id: int) -> int:
        return self.stub.GetStock(inventory_pb2.GetStockRequest(book_id=book_id)).quantity

    def reserve_stock(self, book_id: int, quantity: int) -> bool:
        return self.stub.ReserveStock(inventory_pb2.ReserveStockRequest(book_id=book_id, quantity=quantity)).success

    def release_stock(self, book_id: int, quantity: int) -> bool:
        return self.stub.ReleaseStock(inventory_pb2.ReleaseStockRequest(book_id=book_id, quantity=quantity)).success