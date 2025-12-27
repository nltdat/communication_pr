# Sử dụng Python image chính thức
FROM python:3.11-slim

# Đặt thư mục làm việc trong container
WORKDIR /app

# Ngăn Python tạo file .pyc và bật chế độ unbuffered (log ra stdout ngay)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Cài đặt các dependency hệ thống cần thiết (ví dụ psycopg2, mysqlclient)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements trước để tận dụng cache
COPY requirements.txt /app/

# Cài các package Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code vào container
COPY . /app/

# Expose port (Django mặc định chạy ở 8000)
EXPOSE 8000

# Lệnh khởi chạy Django
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]
