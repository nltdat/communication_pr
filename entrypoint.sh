#!/bin/bash

echo "🚀 Starting Django application..."

# Đợi PostgreSQL sẵn sàng
echo "⏳ Waiting for PostgreSQL..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "✅ PostgreSQL is ready!"

# Đợi MinIO sẵn sàng
echo "⏳ Waiting for MinIO..."
while ! nc -z minio 9000; do
  sleep 0.1
done
echo "✅ MinIO is ready!"

# Chạy migrations
echo "📦 Running migrations..."
python manage.py migrate --noinput

# Khởi tạo MinIO bucket
echo "🗂️ Initializing MinIO bucket..."
python init_minio.py || echo "⚠️ MinIO initialization warning (will retry on first upload)"

# Collect static files (nếu cần)
# python manage.py collectstatic --noinput

# Start server
echo "🎉 Starting Django server..."
python manage.py runserver 0.0.0.0:8000
