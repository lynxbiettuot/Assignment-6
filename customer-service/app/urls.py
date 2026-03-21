from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterView,
    MyProfileView,
    CatalogProxyView,
    CartProxyView,
    OrderProxyView,
    PayProxyView,
    ShipProxyView,
    DashboardDataView,
    CustomTokenObtainPairView,
    login_page,
    register_page,
    dashboard_page,
)

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────────
    path('api/register/',        RegisterView.as_view(),            name='customer_register'),
    path('api/login/',           CustomTokenObtainPairView.as_view(), name='customer_login'),
    path('api/token/refresh/',   TokenRefreshView.as_view(),        name='customer_token_refresh'),

    # ── Profile ───────────────────────────────────────────────────────────────
    path('api/me/',              MyProfileView.as_view(),           name='customer_profile'),

    # ── Proxy views (dùng để điều hướng từ Dashboard) ────────────────────────
    path('api/catalog/',                CatalogProxyView.as_view(), name='customer_catalog_list'),
    path('api/catalog/<path:path>',     CatalogProxyView.as_view(), name='customer_catalog_detail'),
    path('api/cart/',            CartProxyView.as_view(),           name='customer_cart'),
    path('api/orders/',          OrderProxyView.as_view(),          name='customer_orders'),
    path('api/payments/',        PayProxyView.as_view(),            name='customer_payments'),
    path('api/ship/',            ShipProxyView.as_view(),           name='customer_ship'),
    
    # ── Dashboard Data ────────────────────────────────────────────────────────
    path('api/dashboard-data/',  DashboardDataView.as_view(),       name='customer_dashboard_data'),

    # ── HTML Pages ───────────────────────────────────────────────────────────
    path('login/',           login_page,    name='customer_login_page'),
    path('login/register/',  register_page, name='customer_register_page'),
    path('dashboard/',       dashboard_page, name='customer_dashboard_page'),
]
