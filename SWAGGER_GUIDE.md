# 📖 Hướng Dẫn Sử Dụng Swagger API Documentation

## 🌐 Truy Cập Swagger UI

Sau khi start services, bạn có thể truy cập Swagger UI tại:

### **Swagger UI** (Interactive API Documentation)
```
http://localhost:8011/swagger/
```
- Giao diện đẹp, dễ sử dụng
- Test API trực tiếp trên browser
- Xem request/response examples
- Tự động generate từ code

### **ReDoc** (Alternative Documentation)
```
http://localhost:8011/redoc/
```
- Giao diện khác, tập trung vào documentation
- Dễ đọc hơn cho việc tham khảo

### **OpenAPI JSON Schema**
```
http://localhost:8011/swagger.json
```
- Raw OpenAPI 2.0 schema
- Dùng cho các tools khác (Postman, Insomnia, etc.)

---

## 🎯 Các Endpoints Có Sẵn

### 1. **Product CRUD**

#### ✅ GET `/api/products/`
**Lấy danh sách tất cả sản phẩm**
- Response: Array of products với count
- Không cần authentication

#### ✅ POST `/api/products/`
**Tạo sản phẩm mới**
- Body:
  ```json
  {
    "name": "Tên sản phẩm",
    "price": 100000,
    "description": "Mô tả"
  }
  ```
- Response: Product object với ID

#### ✅ GET `/api/products/{id}/`
**Lấy chi tiết một sản phẩm**
- Params: `id` (integer)
- Response: Product object đầy đủ

#### ✅ PUT `/api/products/{id}/`
**Cập nhật toàn bộ sản phẩm**
- Params: `id` (integer)
- Body: Full product data
- Response: Updated product

#### ✅ PATCH `/api/products/{id}/`
**Cập nhật một phần sản phẩm**
- Params: `id` (integer)
- Body: Partial product data
- Response: Updated product

#### ✅ DELETE `/api/products/{id}/`
**Xóa sản phẩm**
- Params: `id` (integer)
- Tự động xóa ảnh trên MinIO
- Response: 204 No Content

---

### 2. **Product Actions**

#### 📸 POST `/api/products/{id}/upload-image/`
**Upload ảnh lên MinIO**
- Content-Type: `multipart/form-data`
- Body: `image` (file)
- Validation:
  - Max size: 5MB
  - Formats: JPG, JPEG, PNG, GIF, WEBP
- Response:
  ```json
  {
    "id": 1,
    "image": "http://localhost:9000/products/products/uuid.jpg",
    "message": "Upload ảnh thành công"
  }
  ```

#### 📝 PATCH `/api/products/{id}/update-description/`
**Cập nhật mô tả sản phẩm**
- Body:
  ```json
  {
    "description": "Mô tả mới"
  }
  ```
- Response: Full product object

#### 🔖 PATCH `/api/products/{id}/update-post-id/`
**Cập nhật post_id (tự động set status = True)**
- Body:
  ```json
  {
    "post_id": "fb_post_12345"
  }
  ```
- Response: Full product object
- Note: `status` sẽ tự động = `true`

#### ⏳ GET `/api/products/pending/`
**Lấy sản phẩm chưa xử lý (status=False)**
- Query sản phẩm có `status = false`
- Response: Array of products với count

---

## 🚀 Cách Sử Dụng Swagger UI

### Bước 1: Mở Swagger UI
```
http://localhost:8011/swagger/
```

### Bước 2: Chọn Endpoint
- Scroll xuống và click vào endpoint muốn test
- VD: `POST /api/products/`

### Bước 3: Click "Try it out"
- Button ở góc phải của endpoint

### Bước 4: Điền Dữ Liệu
- Điền vào request body (nếu cần)
- VD:
  ```json
  {
    "name": "iPhone 15 Pro",
    "price": 29990000,
    "description": "Test product"
  }
  ```

### Bước 5: Click "Execute"
- Swagger sẽ gửi request
- Xem response ở phía dưới

### Bước 6: Xem Response
- **Code**: HTTP status code (200, 201, 400, etc.)
- **Response body**: JSON response
- **Response headers**: Headers trả về

---

## 📸 Test Upload Ảnh Qua Swagger

### Bước 1: Tạo Product
1. Mở endpoint `POST /api/products/`
2. Click "Try it out"
3. Điền thông tin product
4. Execute và lưu lại `id` từ response

### Bước 2: Upload Ảnh
1. Mở endpoint `POST /api/products/{id}/upload-image/`
2. Click "Try it out"
3. Điền `id` vừa tạo vào path parameter
4. Click "Choose File" để chọn ảnh
5. Execute

### Bước 3: Xem Kết Quả
- Response sẽ trả về URL ảnh trên MinIO
- Copy URL và mở trên browser để xem ảnh
- VD: `http://localhost:9000/products/products/uuid-123.jpg`

---

## 💡 Tips & Tricks

### 1. **Schemas/Models**
- Scroll xuống cuối trang Swagger
- Xem section "Schemas" hoặc "Models"
- Tất cả data structures được document ở đây

### 2. **Response Examples**
- Mỗi endpoint có "Example Value" mẫu
- Click để xem structure của request/response

### 3. **Error Codes**
Swagger hiển thị tất cả possible responses:
- ✅ `200` - Success
- ✅ `201` - Created
- ❌ `400` - Bad Request (validation error)
- ❌ `404` - Not Found
- ❌ `500` - Server Error

### 4. **Copy as cURL**
- Sau khi execute, Swagger show cURL command
- Copy để dùng trong terminal

---

## 🔄 Workflow Thực Tế

### Tạo Sản Phẩm Hoàn Chỉnh:

1. **POST** `/api/products/` → Tạo product cơ bản
   ```json
   {
     "name": "iPhone 15",
     "price": 29990000,
     "description": "256GB"
   }
   ```
   → Nhận `id: 1`

2. **POST** `/api/products/1/upload-image/` → Upload ảnh
   - Upload file `iphone15.jpg`
   → Nhận `image: "http://localhost:9000/..."`

3. **PATCH** `/api/products/1/update-description/` → Cập nhật mô tả
   ```json
   {
     "description": "iPhone 15 Pro Max 256GB Natural Titanium"
   }
   ```

4. **PATCH** `/api/products/1/update-post-id/` → Set post_id
   ```json
   {
     "post_id": "fb_123456"
   }
   ```
   → `status` tự động = `true`

5. **GET** `/api/products/1/` → Xem sản phẩm hoàn chỉnh

---

## 🎨 So Sánh: Swagger vs Postman vs cURL

| Feature | Swagger | Postman | cURL |
|---------|---------|---------|------|
| Tích hợp code | ✅ Auto-gen | ❌ Manual | ❌ Manual |
| Interactive UI | ✅ Yes | ✅ Yes | ❌ CLI only |
| Không cần setup | ✅ Built-in | ❌ Need install | ✅ Built-in |
| Documentation | ✅ Auto | ⚠️ Manual | ❌ No |
| File upload | ✅ Easy | ✅ Easy | ⚠️ Complex |
| Share với team | ✅ URL only | ⚠️ Export needed | ⚠️ Command only |

**Kết luận**: Swagger tốt nhất cho development và team collaboration!

---

## 🐛 Troubleshooting

### Lỗi: Static files không load
```bash
docker exec -it communication_api python manage.py collectstatic --noinput
```

### Lỗi: Swagger page trống
- Check logs: `docker logs communication_api`
- Kiểm tra DEBUG=True trong settings
- Restart: `docker-compose restart backend`

### Không thấy custom endpoints
- Đảm bảo decorators `@swagger_auto_schema` đã được thêm
- Rebuild: `docker-compose up -d --build`

### Upload ảnh fail
- Kiểm tra MinIO đã chạy: `docker ps | grep minio`
- Test MinIO: http://localhost:9001
- Check logs: `docker logs communication_minio`

---

## 📚 Tài Liệu Thêm

### Swagger/OpenAPI Spec:
- OpenAPI 2.0: https://swagger.io/specification/v2/
- drf-yasg docs: https://drf-yasg.readthedocs.io/

### Export/Import:
- Export OpenAPI spec: `http://localhost:8011/swagger.json`
- Import vào Postman: File → Import → Paste URL
- Import vào Insomnia: Tương tự

---

## ✨ Các Tính Năng Nâng Cao

### 1. **Custom Tags**
Endpoints được group theo tags trong Swagger UI:
- Products
- Upload
- Status Management

### 2. **Request/Response Examples**
Mỗi endpoint có examples cụ thể với dữ liệu thật

### 3. **Validation Messages**
Errors từ serializers hiển thị rõ ràng trong Swagger

### 4. **File Upload UI**
File upload field với drag-and-drop support

---

## 🎯 Best Practices

1. ✅ **Luôn dùng Swagger để test API mới**
2. ✅ **Share link Swagger với team thay vì viết docs riêng**
3. ✅ **Export OpenAPI spec cho CI/CD**
4. ✅ **Dùng Swagger UI trước khi viết frontend code**
5. ✅ **Check Swagger khi có breaking changes**

---

## 📞 Support

Nếu có vấn đề:
1. Check logs: `docker logs communication_api`
2. Xem API_DOCUMENTATION.md cho chi tiết
3. Test với curl nếu Swagger fail
4. Restart services: `docker-compose restart`

---

**Happy API Testing! 🚀**
