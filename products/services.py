"""
MinIO Service để xử lý upload và quản lý ảnh
"""
import os
import uuid
from datetime import timedelta
from typing import Optional

from minio import Minio
from minio.error import S3Error
from django.conf import settings


class MinioService:
    """Service để tương tác với MinIO"""
    
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Đảm bảo bucket tồn tại, nếu không thì tạo mới"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                # Set bucket policy để public read
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": "*"},
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"]
                        }
                    ]
                }
                import json
                self.client.set_bucket_policy(self.bucket_name, json.dumps(policy))
        except S3Error as e:
            print(f"Error creating bucket: {e}")
    
    def upload_image(self, file, folder: str = "products") -> Optional[str]:
        """
        Upload ảnh lên MinIO
        
        Args:
            file: File object từ request.FILES
            folder: Thư mục lưu trữ trong bucket
            
        Returns:
            URL của ảnh đã upload hoặc None nếu thất bại
        """
        try:
            # Tạo tên file unique
            file_extension = os.path.splitext(file.name)[1]
            unique_filename = f"{folder}/{uuid.uuid4()}{file_extension}"
            
            # Upload file
            self.client.put_object(
                self.bucket_name,
                unique_filename,
                file,
                length=file.size,
                content_type=file.content_type
            )
            
            # Tạo URL public
            image_url = f"{settings.MINIO_PUBLIC_URL}/{self.bucket_name}/{unique_filename}"
            return image_url
            
        except S3Error as e:
            print(f"Error uploading file: {e}")
            return None
    
    def get_presigned_url(self, object_name: str, expiry: int = 3600) -> Optional[str]:
        """
        Tạo presigned URL để download file
        
        Args:
            object_name: Tên object trong bucket
            expiry: Thời gian hết hạn (giây)
            
        Returns:
            Presigned URL hoặc None nếu thất bại
        """
        try:
            url = self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=expiry)
            )
            return url
        except S3Error as e:
            print(f"Error generating presigned URL: {e}")
            return None
    
    def delete_image(self, image_url: str) -> bool:
        """
        Xóa ảnh từ MinIO
        
        Args:
            image_url: URL của ảnh cần xóa
            
        Returns:
            True nếu xóa thành công, False nếu thất bại
        """
        try:
            # Extract object name from URL
            object_name = image_url.split(f"{self.bucket_name}/")[-1]
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            print(f"Error deleting file: {e}")
            return False


# Singleton instance
minio_service = MinioService()
