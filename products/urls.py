from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductHTMLView

# Router cho REST API
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    # HTML view (không phải API)
    path('product/', ProductHTMLView.as_view(), name='product'),
    
    # API endpoints
    path('api/', include(router.urls)),
]
