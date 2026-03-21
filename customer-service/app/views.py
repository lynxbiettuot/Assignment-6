import requests as http_requests
from django.shortcuts import render
from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.models import User

from .models import CustomerProfile
from .serializers import RegisterSerializer, CustomerProfileSerializer


# ── Custom JWT ───────────────────────────────────────────────────────────────

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['role'] = 'customer'
        token['username'] = user.username
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ── Auth Views ────────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    """POST /api/register/ – tạo tài khoản customer mới."""
    queryset            = User.objects.all()
    permission_classes  = (permissions.AllowAny,)
    serializer_class    = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'message': 'Đăng ký thành công.', 'user': RegisterSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


# LoginView & TokenRefreshView are thin wrappers around simplejwt builtins
# (declared in urls.py so they can be customised with extra fields if needed)


# ── Profile View ──────────────────────────────────────────────────────────────

class MyProfileView(APIView):
    """
    GET  /api/me/ – xem hồ sơ của mình
    PUT  /api/me/ – cập nhật toàn bộ
    PATCH /api/me/ – cập nhật một phần
    """
    permission_classes = (permissions.IsAuthenticated,)

    def _get_profile(self, user):
        profile, _ = CustomerProfile.objects.get_or_create(user=user)
        return profile

    def get(self, request):
        profile = self._get_profile(request.user)
        return Response(CustomerProfileSerializer(profile).data)

    def put(self, request):
        profile = self._get_profile(request.user)
        serializer = CustomerProfileSerializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request):
        profile = self._get_profile(request.user)
        serializer = CustomerProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ── Internal Proxy Helper ─────────────────────────────────────────────────────

def _proxy_request(request, upstream_url, extra_params=None):
    """
    Forward request tới upstream service, đính kèm X-User-Id và X-User-Role.
    extra_params được merge vào query string.
    """
    params = dict(request.GET)
    if extra_params:
        params.update(extra_params)

    headers = {
        'X-User-Id':   str(request.user.id),
        'X-User-Role': 'customer',
    }
    # Forward Authorization header so downstream can also verify if needed
    auth = request.headers.get('Authorization')
    if auth:
        headers['Authorization'] = auth

    try:
        resp = http_requests.get(
            upstream_url,
            params=params,
            headers=headers,
            timeout=10,
        )
        return Response(resp.json(), status=resp.status_code)
    except http_requests.exceptions.RequestException as exc:
        return Response({'error': f'Upstream error: {str(exc)}'}, status=status.HTTP_502_BAD_GATEWAY)


# ── Proxy Views ───────────────────────────────────────────────────────────────

class CatalogProxyView(APIView):
    """GET /api/catalog/[<path>/] – xem danh sách sách (read-only, public catalog)."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, path=''):
        base = settings.CATALOG_SERVICE_URL.rstrip('/')
        upstream_url = f"{base}/books/{path}" if path else f"{base}/books/"
        return _proxy_request(request, upstream_url)


class CartProxyView(APIView):
    """GET /api/cart/ – xem giỏ hàng của chính mình (filter theo user_id từ token)."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # Service cart dùng pattern: /carts/<customer_id>/
        upstream_url = f"{settings.CART_SERVICE_URL.rstrip('/')}/carts/{request.user.id}/"
        return _proxy_request(request, upstream_url)


class OrderProxyView(APIView):
    """GET /api/orders/ – xem đơn hàng của chính mình."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # Service order dùng pattern: /orders/users/<customer_id>/
        upstream_url = f"{settings.ORDER_SERVICE_URL.rstrip('/')}/orders/users/{request.user.id}/"
        return _proxy_request(request, upstream_url)


class PayProxyView(APIView):
    """GET /api/payments/ – xem lịch sử thanh toán của chính mình."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        upstream_url = f"{settings.PAY_SERVICE_URL.rstrip('/')}/payments/"
        return _proxy_request(request, upstream_url, extra_params={'user_id': request.user.id})


class ShipProxyView(APIView):
    """GET /api/ship/ – xem thông tin vận chuyển của chính mình."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # Service ship dùng /shipping/all/ kết hợp query param customer_id
        upstream_url = f"{settings.SHIP_SERVICE_URL.rstrip('/')}/shipping/all/"
        return _proxy_request(request, upstream_url, extra_params={'customer_id': request.user.id})


# ── HTML Page Views ───────────────────────────────────────────────────────────

def login_page(request):
    """GET /login/ – trang đăng nhập HTML."""
    return render(request, 'login.html')


def register_page(request):
    """GET /login/register/ – trang đăng ký HTML."""
    return render(request, 'register.html')


def dashboard_page(request):
    """GET /dashboard/ – trang Dashboard chính."""
    return render(request, 'dashboard.html')


class DashboardDataView(APIView):
    """
    GET /api/dashboard-data/ – lấy tổng hợp dữ liệu cho Dashboard.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user_id = request.user.id
        headers = {
            'X-User-Id': str(user_id),
            'X-User-Role': 'customer',
            'Authorization': request.headers.get('Authorization')
        }

        # 1. Lấy dữ liệu giỏ hàng
        cart_data = []
        try:
            cart_resp = http_requests.get(
                f"{settings.CART_SERVICE_URL.rstrip('/')}/carts/{user_id}/",
                headers=headers,
                timeout=5
            )
            if cart_resp.status_code == 200:
                cart_data = cart_resp.json()
        except: pass

        # 2. Lấy dữ liệu đơn hàng
        orders_data = []
        try:
            orders_resp = http_requests.get(
                f"{settings.ORDER_SERVICE_URL.rstrip('/')}/orders/users/{user_id}/",
                headers=headers,
                timeout=5
            )
            if orders_resp.status_code == 200:
                orders_data = orders_resp.json()
        except: pass

        # 3. Lấy tổng số sách (từ Catalog)
        total_books = 0
        try:
            catalog_resp = http_requests.get(
                f"{settings.CATALOG_SERVICE_URL.rstrip('/')}/books/",
                headers=headers,
                timeout=5
            )
            if catalog_resp.status_code == 200:
                books = catalog_resp.json()
                total_books = len(books)
        except: pass

        return Response({
            'cart_count': len(cart_data),
            'order_count': len(orders_data),
            'total_available_books': total_books,
            'recent_orders': orders_data[:5],
            'recent_cart_items': cart_data[:5]
        })

from .serializers import CustomerManagerSerializer

class CustomerListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomerManagerSerializer
    permission_classes = [permissions.IsAuthenticated]

class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = CustomerManagerSerializer
    permission_classes = [permissions.IsAuthenticated]

