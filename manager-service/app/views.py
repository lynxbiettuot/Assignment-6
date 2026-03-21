from django.contrib.auth.models import User
import requests
from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = 'manager'
        token['username'] = user.username
        return token

class ManagerLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ManagerRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        
        if not username or not password:
            return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.create_user(username=username, email=email, password=password)
        # For simplicity in this demo, every registered user here is a manager
        user.is_staff = True 
        user.save()
        
        return Response({'message': 'Manager created successfully'}, status=status.HTTP_201_CREATED)

class DashboardDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        headers = {'Authorization': request.headers.get('Authorization')}
        
        # 1. Total active books
        total_books = 0
        try:
            r = requests.get(f"{settings.CATALOG_SERVICE_URL}/catalog/books/", timeout=5)
            if r.status_code == 200:
                data = r.json()
                # CatalogListView returns paginated response: {"count": X, "results": [...]}
                if isinstance(data, dict) and 'count' in data:
                    total_books = data['count']
                else:
                    total_books = len(data)
        except Exception: pass
        
        # 2. Total staff
        total_staff = 0
        try:
            r = requests.get(f"{settings.STAFF_SERVICE_URL}/api/users/", headers=headers, timeout=5)
            if r.status_code == 200:
                total_staff = len(r.json())
        except Exception: pass
        
        # 3. Total customers
        total_customers = 0
        try:
            r = requests.get(f"{settings.CUSTOMER_SERVICE_URL}/api/users/", headers=headers, timeout=5)
            if r.status_code == 200:
                total_customers = len(r.json())
        except Exception: pass
        
        # 4. Total revenue (Shipping Success)
        revenue = 0
        try:
            ship_r = requests.get(f"{settings.SHIP_SERVICE_URL}/shipping/all/", headers=headers, timeout=5)
            if ship_r.status_code == 200:
                shippings = ship_r.json()
                successful_order_ids = [s['order_id'] for s in shippings if s.get('status') == 'Success']
                
                if successful_order_ids:
                    order_r = requests.get(f"{settings.ORDER_SERVICE_URL}/orders/all/", headers=headers, timeout=5)
                    if order_r.status_code == 200:
                        orders = order_r.json()
                        for order in orders:
                            if order['id'] in successful_order_ids:
                                revenue += float(order.get('total_price', 0))
        except Exception: pass

        return Response({
            'total_books': total_books,
            'total_staff': total_staff,
            'total_customers': total_customers,
            'total_revenue': float(revenue)
        })

class GeneralProxyView(APIView):
    permission_classes = [permissions.IsAuthenticated]
        
    def _proxy(self, request, method, pk=None):
        headers = {'Authorization': request.headers.get('Authorization')}
        base_url = self.kwargs.get('base_url')
        
        target_url = f"{base_url}{pk}/" if pk else base_url
        
        try:
            res = requests.request(
                method,
                target_url,
                json=request.data if method in ['POST', 'PUT', 'PATCH'] else None,
                params=request.GET,
                headers=headers
            )
            try:
                data = res.json()
            except:
                data = res.text
            return Response(data, status=res.status_code)
        except Exception as e:
            return Response({'error': str(e)}, status=502)

    def get(self, request, pk=None, *args, **kwargs): return self._proxy(request, 'GET', pk)
    def post(self, request, pk=None, *args, **kwargs): return self._proxy(request, 'POST', pk)
    def put(self, request, pk=None, *args, **kwargs): return self._proxy(request, 'PUT', pk)
    def delete(self, request, pk=None, *args, **kwargs): return self._proxy(request, 'DELETE', pk)

class BookEditProxyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        headers = {'Authorization': request.headers.get('Authorization')}
        data = request.POST.dict()
        files = {}
        for key, f in request.FILES.items():
            files[key] = (f.name, f.read(), f.content_type)
            
        try:
            res = requests.put(
                f"{settings.BOOK_SERVICE_URL}/books/{pk}/",
                headers=headers,
                data=data,
                files=files
            )
            return Response(res.json(), status=res.status_code)
        except Exception as e:
            return Response({'error': str(e)}, status=502)
