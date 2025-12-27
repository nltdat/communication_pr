from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.views import View

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Product
from .serializers import (
    ProductSerializer,
    ProductCreateSerializer,
    ProductImageUploadSerializer,
    ProductUpdateDescriptionSerializer,
    ProductUpdatePostIdSerializer,
    ProductListSerializer,
)
from .services import minio_service


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet cho Product API
    
    Cung cấp các endpoints để quản lý sản phẩm và upload ảnh lên MinIO storage.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        """Chọn serializer phù hợp cho từng action"""
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        elif self.action == 'upload_image':
            return ProductImageUploadSerializer
        elif self.action == 'update_description':
            return ProductUpdateDescriptionSerializer
        elif self.action == 'update_post_id':
            return ProductUpdatePostIdSerializer
        return ProductSerializer
    
    @swagger_auto_schema(
        operation_summary="Tạo sản phẩm mới",
        operation_description="""
        Tạo một sản phẩm mới với thông tin cơ bản.
        Sau khi tạo, bạn có thể upload ảnh qua endpoint upload-image.
        """,
        request_body=ProductCreateSerializer,
        responses={
            201: openapi.Response(
                description="Tạo sản phẩm thành công",
                schema=ProductSerializer
            ),
            400: "Bad Request - Dữ liệu không hợp lệ"
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Tạo sản phẩm mới
        POST /api/products/
        Body: {
            "name": "Tên sản phẩm",
            "price": 100000,
            "description": "Mô tả sản phẩm"
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Tạo product với các giá trị mặc định
        product = Product.objects.create(
            name=serializer.validated_data['name'],
            price=serializer.validated_data['price'],
            description=serializer.validated_data.get('description', ''),
            image='',
            post_id='',
            status=False
        )
        
        # Trả về response với serializer đầy đủ
        response_serializer = ProductSerializer(product)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @swagger_auto_schema(
        operation_summary="Lấy danh sách sản phẩm",
        operation_description="Lấy danh sách tất cả sản phẩm trong hệ thống",
        responses={
            200: openapi.Response(
                description="Danh sách sản phẩm",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Tổng số sản phẩm'),
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT, ref='#/definitions/ProductList')
                        )
                    }
                )
            )
        }
    )
    def list(self, request, *args, **kwargs):
        """
        Lấy danh sách tất cả sản phẩm
        GET /api/products/
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    @swagger_auto_schema(
        operation_summary="Lấy chi tiết sản phẩm",
        operation_description="Lấy thông tin chi tiết của một sản phẩm theo ID",
        responses={
            200: ProductSerializer,
            404: "Không tìm thấy sản phẩm"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Lấy chi tiết một sản phẩm
        GET /api/products/{id}/
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """
        Cập nhật toàn bộ thông tin sản phẩm
        PUT /api/products/{id}/
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        Xóa sản phẩm
        DELETE /api/products/{id}/
        """
        instance = self.get_object()
        
        # Xóa ảnh trên MinIO nếu có
        if instance.image:
            minio_service.delete_image(instance.image)
        
        self.perform_destroy(instance)
        return Response(
            {'message': 'Đã xóa sản phẩm thành công'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['post'], url_path='upload-image')
    @swagger_auto_schema(
        operation_summary="Upload ảnh cho sản phẩm",
        operation_description="""
        Upload ảnh lên MinIO storage và lưu URL vào database.
        
        **Yêu cầu:**
        - File size: Max 5MB
        - Format: JPG, JPEG, PNG, GIF, WEBP
        
        **Flow:**
        1. Upload file lên MinIO
        2. Nhận public URL từ MinIO
        3. Lưu URL vào database
        4. Xóa ảnh cũ (nếu có)
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['image'],
            properties={
                'image': openapi.Schema(
                    type=openapi.TYPE_FILE,
                    description='File ảnh cần upload (max 5MB, jpg/png/gif/webp)'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Upload thành công",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Product ID'),
                        'image': openapi.Schema(type=openapi.TYPE_STRING, description='URL ảnh trên MinIO'),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Thông báo'),
                    }
                )
            ),
            400: "Bad Request - File không hợp lệ",
            500: "Internal Server Error - Lỗi upload lên MinIO"
        }
    )
    def upload_image(self, request, pk=None):
        """
        Upload ảnh cho sản phẩm
        POST /api/products/{id}/upload-image/
        Body (form-data):
            image: file
        
        Response: {
            "id": 1,
            "image": "http://localhost:9000/products/products/uuid.jpg",
            "message": "Upload ảnh thành công"
        }
        """
        product = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Upload ảnh lên MinIO
        image_file = serializer.validated_data['image']
        image_url = minio_service.upload_image(image_file)  # Bỏ folder parameter
        
        if not image_url:
            return Response(
                {'error': 'Không thể upload ảnh lên MinIO'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Xóa ảnh cũ nếu có
        if product.image:
            minio_service.delete_image(product.image)
        
        # Cập nhật link ảnh vào database
        product.image = image_url
        product.save()
        
        return Response({
            'id': product.id,
            'image': image_url,
            'message': 'Upload ảnh thành công'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['patch'], url_path='update-description')
    @swagger_auto_schema(
        operation_summary="Cập nhật mô tả sản phẩm",
        operation_description="Cập nhật mô tả chi tiết cho sản phẩm",
        request_body=ProductUpdateDescriptionSerializer,
        responses={
            200: ProductSerializer,
            400: "Bad Request - Dữ liệu không hợp lệ",
            404: "Không tìm thấy sản phẩm"
        }
    )
    def update_description(self, request, pk=None):
        """
        Cập nhật mô tả sản phẩm
        PATCH /api/products/{id}/update-description/
        Body: {
            "description": "Mô tả mới"
        }
        """
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Trả về dữ liệu đầy đủ
        response_serializer = ProductSerializer(product)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['patch'], url_path='update-post-id')
    @swagger_auto_schema(
        operation_summary="Cập nhật post_id và kích hoạt sản phẩm",
        operation_description="""
        Cập nhật post_id cho sản phẩm.
        
        **Lưu ý:** Khi cập nhật post_id, status sẽ tự động được set thành True.
        """,
        request_body=ProductUpdatePostIdSerializer,
        responses={
            200: ProductSerializer,
            400: "Bad Request - post_id không được để trống",
            404: "Không tìm thấy sản phẩm"
        }
    )
    def update_post_id(self, request, pk=None):
        """
        Cập nhật post_id và tự động set status = True
        PATCH /api/products/{id}/update-post-id/
        Body: {
            "post_id": "12345"
        }
        """
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Tự động cập nhật status = True khi có post_id
        product.status = True
        product.save()
        
        # Trả về dữ liệu đầy đủ
        response_serializer = ProductSerializer(product)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='pending')
    @swagger_auto_schema(
        operation_summary="Lấy danh sách sản phẩm chưa xử lý",
        operation_description="""
        Lấy danh sách các sản phẩm có status = False (chưa được post).
        
        Các sản phẩm này thường là:
        - Sản phẩm mới tạo chưa có post_id
        - Sản phẩm chưa được đăng lên platform
        """,
        responses={
            200: openapi.Response(
                description="Danh sách sản phẩm pending",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Số lượng sản phẩm pending'),
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT, ref='#/definitions/ProductList')
                        )
                    }
                )
            )
        }
    )
    def pending_products(self, request):
        """
        Lấy danh sách sản phẩm chưa xử lý (status = False)
        GET /api/products/pending/
        """
        pending_products = Product.objects.filter(status=False)
        serializer = ProductListSerializer(pending_products, many=True)
        return Response({
            'count': pending_products.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)


# ---- HTML view riêng (không nằm trong ViewSet) ----
class ProductHTMLView(View):
    """View HTML để tạo và hiển thị sản phẩm"""
    
    def get(self, request):
        products = Product.objects.all()
        template = loader.get_template('product_form.html')
        return HttpResponse(template.render({'products': products}, request))

    def post(self, request):
        name = request.POST.get('name')
        price = request.POST.get('price')

        if name and price:
            Product.objects.create(
                name=name,
                price=int(price),
                description='',
                image='',
                post_id=''
            )
            return redirect('product')

        products = Product.objects.all()
        template = loader.get_template('product_form.html')
        context = {
            'error': 'Vui lòng điền đầy đủ thông tin',
            'products': products
        }
        return HttpResponse(template.render(context, request))

