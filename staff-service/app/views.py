import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class StaffDashboardDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # 1. Lấy tổng số sách từ Catalog Service
            books_res = requests.get(f"{settings.CATALOG_SERVICE_URL}/catalog/books/")
            total_books = 0
            if books_res.ok:
                total_books = books_res.json().get('count', 0)

            # 2. Lấy danh sách ship để thống kê
            ship_res = requests.get(f"{settings.SHIP_SERVICE_URL}/shipping/all/")
            shipping_orders = []
            if ship_res.ok:
                shipping_orders = ship_res.json()

            shipping_count = len([s for s in shipping_orders if s.get('status') == 'Processing'])
            delivered_count = len([s for s in shipping_orders if s.get('status') in ['Delivered', 'Success']])

            return Response({
                "total_products": total_books,
                "shipping_count": shipping_count,
                "delivered_count": delivered_count
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class StaffShipProxyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Lấy tất cả shipping cho staff xem
        res = requests.get(f"{settings.SHIP_SERVICE_URL}/shipping/all/")
        return Response(res.json(), status=res.status_code)

class StaffShipStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        # Cập nhật trạng thái thành 'Success'
        res = requests.put(
            f"{settings.SHIP_SERVICE_URL}/shipping/status/{pk}/",
            json={"status": "Success"}
        )
        return Response(res.json(), status=res.status_code)

class StaffCatalogProxyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Forward ALL query parameters (page, search, sort, тощо) explicitly
        query_params = request.GET.dict()
        res = requests.get(
            f"{settings.CATALOG_SERVICE_URL}/catalog/books/",
            params=query_params
        )
        return Response(res.json(), status=res.status_code)

from django.contrib.auth.models import User
from rest_framework import status

class RegisterStaffView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        return Response({"message": "Staff user created successfully"}, status=status.HTTP_201_CREATED)

class StaffBookCreateProxyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Extract files properly for requests
        files = {key: (file.name, file, file.content_type) for key, file in request.FILES.items()}
        # Extract data
        data = {key: value for key, value in request.POST.items()}
        
        res = requests.post(
            f"{settings.BOOK_SERVICE_URL}/books/",
            data=data,
            files=files
        )
        return Response(res.json(), status=res.status_code)

from rest_framework import generics
from .serializers import UserSerializer

class StaffListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class StaffDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
