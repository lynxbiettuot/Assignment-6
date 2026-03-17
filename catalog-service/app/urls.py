from django.urls import path
from .views import CatalogListView, CatalogDetailView

urlpatterns = [
    # Gateway routes reads targeting /catalog/ prefix to catalog-service
    path('catalog/books/', CatalogListView.as_view(), name='catalog-list'),
    path('catalog/books/<int:pk>/', CatalogDetailView.as_view(), name='catalog-detail'),
]
