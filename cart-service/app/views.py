from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
import requests

BOOK_SERVICE_URL = "http://book-service:8000"

class CartCreate(APIView):
    def post(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

class AddCartItem(APIView):
    def post(self, request):
        book_id = request.data.get("book_id")
        try:
            r = requests.get(f"{BOOK_SERVICE_URL}/books/")
            r.raise_for_status()
            books = r.json()
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Failed to connect to book service: {e}"})

        if not any(b["id"] == int(book_id) for b in books):
            return Response({"error": "Book not found"})

        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

class ViewCart(APIView):
    def get(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            items = CartItem.objects.filter(cart=cart)
            serializer = CartItemSerializer(items, many=True)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"})

class ClearCart(APIView):
    def delete(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            CartItem.objects.filter(cart=cart).delete()
            return Response({"message": "Cart cleared successfully"})
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=404)
