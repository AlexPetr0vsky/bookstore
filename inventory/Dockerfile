FROM python:3.12-slim

RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY inventory/ ./inventory/
COPY . .

WORKDIR /app/inventory

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. inventory.proto

EXPOSE 50051

CMD ["python", "server.py"]