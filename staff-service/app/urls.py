from django.urls import path
from .views import StaffDashboardDataView, StaffShipProxyView, StaffShipStatusUpdateView, StaffCatalogProxyView, RegisterStaffView, StaffBookCreateProxyView
from .views import StaffListCreateView, StaffDetailView

urlpatterns = [
    path('dashboard-data/', StaffDashboardDataView.as_view(), name='staff-dashboard-data'),
    path('ship/', StaffShipProxyView.as_view(), name='staff-ship-all'),
    path('ship/status/<int:pk>/', StaffShipStatusUpdateView.as_view(), name='staff-ship-update'),
    path('catalog/', StaffCatalogProxyView.as_view(), name='staff-catalog-proxy'),
    path('books/create/', StaffBookCreateProxyView.as_view(), name='staff-book-create'),
    path('register/', RegisterStaffView.as_view(), name='staff-register'),
    path('users/', StaffListCreateView.as_view(), name='staff-users-list'),
    path('users/<int:pk>/', StaffDetailView.as_view(), name='staff-users-detail'),
]
