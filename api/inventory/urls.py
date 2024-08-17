from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryItemViewSet
from .views import inventory_api_view


router = DefaultRouter()
router.register(r'inventory', InventoryItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/inventory/', inventory_api_view, name='inventory_api'),
]