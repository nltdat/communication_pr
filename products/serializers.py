from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    """Serializer đầy đủ cho Product"""
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'status', 'image', 'post_id']
        read_only_fields = ['id']

class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer để tạo Product mới"""
    class Meta:
        model = Product
        fields = ['name', 'price', 'description']
    
    def validate_price(self, value):
        """Validate giá phải lớn hơn 0"""
        if value <= 0:
            raise serializers.ValidationError("Giá sản phẩm phải lớn hơn 0")
        return value

class ProductImageUploadSerializer(serializers.Serializer):
    """Serializer để upload ảnh cho Product"""
    image = serializers.ImageField(required=True)
    
    def validate_image(self, value):
        """Validate image file"""
        # Kiểm tra kích thước file (max 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Kích thước ảnh không được vượt quá 5MB")
        
        # Kiểm tra định dạng file
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"Định dạng file không hợp lệ. Chỉ chấp nhận: {', '.join(allowed_extensions)}"
            )
        
        return value

class ProductUpdateDescriptionSerializer(serializers.ModelSerializer):
    """Serializer để cập nhật description"""
    class Meta:
        model = Product
        fields = ['description']

class ProductUpdatePostIdSerializer(serializers.ModelSerializer):
    """Serializer để cập nhật post_id"""
    class Meta:
        model = Product
        fields = ['post_id']
    
    def validate_post_id(self, value):
        """Validate post_id không được rỗng"""
        if not value or not value.strip():
            raise serializers.ValidationError("Post ID không được để trống")
        return value

class ProductListSerializer(serializers.ModelSerializer):
    """Serializer cho list view - ẩn một số thông tin nhạy cảm"""
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'status', 'image']
