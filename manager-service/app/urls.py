from django.urls import path
from django.conf import settings
from .views import ManagerLoginView, ManagerRegisterView, DashboardDataView, GeneralProxyView, BookEditProxyView

urlpatterns = [
    path('login/', ManagerLoginView.as_view(), name='manager-login'),
    path('register/', ManagerRegisterView.as_view(), name='manager-register'),
    path('dashboard-data/', DashboardDataView.as_view(), name='manager-dashboard-data'),
    
    # Proxy for Staff CRUD
    path('staff/', GeneralProxyView.as_view(), kwargs={'base_url': f"{settings.STAFF_SERVICE_URL}/api/users/"}, name='manager-staff-list'),
    path('staff/<int:pk>/', GeneralProxyView.as_view(), kwargs={'base_url': f"{settings.STAFF_SERVICE_URL}/api/users/"}, name='manager-staff-detail'),
    
    # Proxy for Catalog (View Books)
    path('catalog/', GeneralProxyView.as_view(), {'base_url': f"{settings.CATALOG_SERVICE_URL}/catalog/books/"}, name='manager-catalog-proxy'),
    path('catalog/<int:pk>/', GeneralProxyView.as_view(), {'base_url': f"{settings.CATALOG_SERVICE_URL}/catalog/books/"}, name='manager-catalog-detail-proxy'),
    
    # Proxy for Customer CRUD
    path('customers/', GeneralProxyView.as_view(), kwargs={'base_url': f"{settings.CUSTOMER_SERVICE_URL}/api/users/"}, name='manager-customer-list'),
    path('customers/<int:pk>/', GeneralProxyView.as_view(), kwargs={'base_url': f"{settings.CUSTOMER_SERVICE_URL}/api/users/"}, name='manager-customer-detail'),
    
    path('catalog/', GeneralProxyView.as_view(), kwargs={'base_url': f"{settings.CATALOG_SERVICE_URL}/books/"}, name='manager-catalog-list'),
    
    # Proxy for Book Editing (PUT with Image)
    path('books/<int:pk>/', BookEditProxyView.as_view(), name='manager-book-edit'),
]
