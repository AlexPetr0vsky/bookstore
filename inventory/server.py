import grpc
from concurrent import futures
import inventory_pb2
import inventory_pb2_grpc
import db


class InventoryService(inventory_pb2_grpc.InventoryServiceServicer):
    def GetStock(self, request, context):
        quantity = db.get_stock(request.book_id)
        return inventory_pb2.GetStockResponse(
            book_id=request.book_id,
            quantity=quantity
        )

    def ReserveStock(self, request, context):
        success = db.reserve_stock(request.book_id, request.quantity)
        return inventory_pb2.ReserveStockResponse(
            success=success,
            message="Reserved" if success else "Not enough stock"
        )

    def ReleaseStock(self, request, context):
        db.release_stock(request.book_id, request.quantity)
        return inventory_pb2.ReleaseStockResponse(
            success=True,
            message="Released"
        )


def serve():
    db.init_db()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inventory_pb2_grpc.add_InventoryServiceServicer_to_server(
        InventoryService(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Inventory gRPC server started on port 50051")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
