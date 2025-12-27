# 🚀 Product API with MinIO Storage

API quản lý sản phẩm với tích hợp MinIO storage service và Swagger documentation.

## ✨ Tính Năng

- ✅ **REST API** chuẩn với Django REST Framework
- ✅ **MinIO Storage** - Cloud storage cho ảnh sản phẩm
- ✅ **Swagger UI** - Interactive API documentation
- ✅ **PostgreSQL** - Database
- ✅ **Docker** - Containerized deployment
- ✅ **n8n** - Workflow automation (optional)

---

## 🎯 Quick Start

### 1. Clone và Start Services

```bash
# Clone repository (nếu cần)
git clone <repo-url>
cd communication_pr

# Build và start tất cả services
docker-compose up -d --build

# Xem logs
docker-compose logs -f backend
```

### 2. Collect Static Files (lần đầu)

```bash
docker exec -it communication_api python manage.py collectstatic --noinput
```

### 3. Truy Cập Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Swagger UI** 🔥 | http://localhost:8011/swagger/ | - |
| **ReDoc** | http://localhost:8011/redoc/ | - |
| **API Endpoint** | http://localhost:8011/api/products/ | - |
| **MinIO Console** | http://localhost:9001 | minioadmin/minioadmin123 |
| **PgAdmin** | http://localhost:5080 | admin@example.com/admin123 |
| **n8n** | http://localhost:5678 | admin/admin |

---

## 📖 API Documentation

### 🌟 Swagger UI (RECOMMENDED)

Truy cập: **http://localhost:8011/swagger/**

Swagger UI cung cấp:
- ✅ Interactive API testing
- ✅ Tất cả endpoints với examples
- ✅ Upload file trực tiếp
- ✅ Request/Response schemas
- ✅ Try-it-out feature

**→ Xem hướng dẫn chi tiết tại: [`SWAGGER_GUIDE.md`](SWAGGER_GUIDE.md)**

---

## 🎯 API Endpoints

### Products CRUD

```
GET     /api/products/              # Lấy danh sách
POST    /api/products/              # Tạo mới
GET     /api/products/{id}/         # Chi tiết
PUT     /api/products/{id}/         # Cập nhật toàn bộ
PATCH   /api/products/{id}/         # Cập nhật một phần
DELETE  /api/products/{id}/         # Xóa
```

### Actions

```
POST    /api/products/{id}/upload-image/        # Upload ảnh lên MinIO
PATCH   /api/products/{id}/update-description/  # Cập nhật mô tả
PATCH   /api/products/{id}/update-post-id/      # Cập nhật post_id
GET     /api/products/pending/                  # Lấy pending products
```

---

## 🔥 Demo Nhanh

### 1. Test qua Swagger UI (Recommended)

```
1. Mở: http://localhost:8011/swagger/
2. Chọn endpoint "POST /api/products/"
3. Click "Try it out"
4. Điền dữ liệu và click "Execute"
5. Xem response
```

### 2. Test qua cURL

```bash
# 1. Tạo sản phẩm
curl -X POST http://localhost:8011/api/products/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iPhone 15 Pro",
    "price": 29990000,
    "description": "iPhone 15 Pro 256GB"
  }'

# 2. Upload ảnh (thay {id})
curl -X POST http://localhost:8011/api/products/1/upload-image/ \
  -F "image=@/path/to/image.jpg"

# 3. Lấy pending products
curl http://localhost:8011/api/products/pending/
```

### 3. Test qua Python

```bash
pip install requests
python test_api.py
```

---

## 📸 Upload Ảnh Flow

```
1. Tạo product          → POST /api/products/
2. Upload ảnh           → POST /api/products/{id}/upload-image/
3. MinIO lưu ảnh        → Trả về public URL
4. URL lưu vào DB       → field 'image'
5. Truy cập ảnh         → http://localhost:9000/products/products/{uuid}.jpg
```

**Validation:**
- Max size: 5MB
- Formats: JPG, JPEG, PNG, GIF, WEBP

---

## 🗂️ Cấu Trúc Project

```
communication_pr/
├── communication_pr/          # Django project settings
│   ├── settings.py           # Cấu hình chính
│   └── urls.py              # Swagger config
├── products/                 # Products app
│   ├── models.py            # Product model
│   ├── serializers.py       # API serializers (với validation)
│   ├── views.py             # API ViewSet (với Swagger docs)
│   ├── services.py          # MinIO service
│   └── urls.py              # Products routing
├── docker-compose.yml        # Services definition
├── Dockerfile               # Backend image
├── requirements.txt         # Python dependencies
├── test_api.py             # Test script
├── SWAGGER_GUIDE.md        # Hướng dẫn Swagger
└── API_DOCUMENTATION.md    # API docs chi tiết
```

---

## 🔧 Các Lệnh Hữu Ích

### Docker Management

```bash
# Stop tất cả
docker-compose down

# Stop và xóa volumes (xóa data)
docker-compose down -v

# Restart một service
docker-compose restart backend

# Xem logs realtime
docker-compose logs -f backend

# Vào shell của container
docker exec -it communication_api bash
```

### Django Commands

```bash
# Chạy migrations
docker exec -it communication_api python manage.py migrate

# Tạo migrations mới
docker exec -it communication_api python manage.py makemigrations

# Collect static files
docker exec -it communication_api python manage.py collectstatic --noinput

# Tạo superuser
docker exec -it communication_api python manage.py createsuperuser

# Django shell
docker exec -it communication_api python manage.py shell
```

### MinIO

```bash
# Test MinIO service
docker exec -it communication_api python init_minio.py

# Xem MinIO logs
docker logs communication_minio
```

---

## 🐛 Troubleshooting

### 1. Container không start

```bash
# Check logs
docker logs communication_api

# Check tất cả containers
docker-compose ps

# Restart
docker-compose restart
```

### 2. Swagger UI không load CSS

```bash
# Collect static files
docker exec -it communication_api python manage.py collectstatic --noinput
docker-compose restart backend
```

### 3. MinIO không kết nối

```bash
# Check MinIO
docker logs communication_minio

# Restart MinIO
docker-compose restart minio

# Test connection
docker exec -it communication_api python -c "from products.services import minio_service; print(minio_service.client.bucket_exists('products'))"
```

### 4. Import errors (minio, drf-yasg)

```bash
# Rebuild với dependencies mới
docker-compose down
docker-compose up -d --build
```

### 5. Database connection errors

```bash
# Check PostgreSQL
docker logs communication_db

# Restart database
docker-compose restart postgres

# Run migrations lại
docker exec -it communication_api python manage.py migrate
```

---

## 📚 Documentation Files

| File | Description |
|------|-------------|
| [`SWAGGER_GUIDE.md`](SWAGGER_GUIDE.md) | 🔥 Hướng dẫn chi tiết Swagger UI |
| [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md) | Chi tiết tất cả API endpoints |
| [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md) | Technical overview |
| `test_api.py` | Python test script |

---

## 🎨 Technology Stack

- **Backend**: Django 5.2.7 + Django REST Framework 3.16.1
- **Database**: PostgreSQL 15
- **Storage**: MinIO (S3-compatible)
- **API Docs**: drf-yasg (Swagger/OpenAPI)
- **Containerization**: Docker + Docker Compose
- **Automation**: n8n

---

## 🌟 Features Highlights

### 1. **RESTful API**
- Standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Proper status codes
- JSON responses
- Error handling

### 2. **MinIO Integration**
- S3-compatible object storage
- Public URL generation
- Automatic bucket creation
- File validation (size, format)

### 3. **Swagger Documentation**
- Auto-generated from code
- Interactive testing
- Request/Response examples
- No manual documentation needed

### 4. **Validation**
- Image: size (max 5MB), format (jpg, png, gif, webp)
- Price: must be > 0
- Post ID: not empty
- All fields properly validated

---

## 🚀 Production Checklist

Trước khi deploy lên production:

- [ ] Change `DEBUG = False` in settings.py
- [ ] Set strong `SECRET_KEY`
- [ ] Change MinIO credentials
- [ ] Enable `MINIO_USE_SSL = True`
- [ ] Configure domain for MinIO
- [ ] Set `ALLOWED_HOSTS` properly
- [ ] Use production WSGI server (gunicorn/uwsgi)
- [ ] Enable HTTPS
- [ ] Configure backup for PostgreSQL
- [ ] Configure backup for MinIO
- [ ] Set up monitoring
- [ ] Configure CORS if needed

---

## 📝 License

[Your License Here]

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repo
2. Create a feature branch
3. Make changes
4. Test thoroughly (use Swagger!)
5. Submit pull request

---

## 📞 Support

- Issues: [GitHub Issues](your-repo-url/issues)
- Documentation: Check `.md` files in this repo
- Swagger: http://localhost:8011/swagger/

---

**Built with ❤️ using Django REST Framework + MinIO + Swagger**
