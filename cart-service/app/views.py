from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
import requests

BOOK_SERVICE_URL = "http://book-service:8000"

class CartCreate(APIView):
    def post(self, request):
        customer_id = request.data.get("customer_id")
        if not customer_id:
            return Response({"error": "customer_id is required"}, status=400)
        
        cart, created = Cart.objects.get_or_create(customer_id=customer_id)
        serializer = CartSerializer(cart)
        status_code = 201 if created else 200
        return Response(serializer.data, status=status_code)

class AddCartItem(APIView):
    def post(self, request):
        book_id = request.data.get("book_id")
        if not book_id:
            return Response({"error": "book_id is required"}, status=400)
            
        try:
            # Using the new detail endpoint we added to book-service
            r = requests.get(f"{BOOK_SERVICE_URL}/books/{book_id}/", timeout=5)
            if r.status_code == 404:
                return Response({"error": "Book not found in database"}, status=404)
            r.raise_for_status()
            book_data = r.json()
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Failed to connect to book service: {str(e)}"}, status=502)

        # Proceed to save the item
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class ViewCart(APIView):
    def get(self, request, customer_id):
        try:
            # Using filter().first() as a safety measure, though customer_id is now unique
            cart = Cart.objects.filter(customer_id=customer_id).first()
            if not cart:
                return Response([], status=200) # Return empty list if no cart
            
            items = CartItem.objects.filter(cart=cart)
            serializer = CartItemSerializer(items, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class ClearCart(APIView):
    def delete(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            CartItem.objects.filter(cart=cart).delete()
            return Response({"message": "Cart cleared successfully"})
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=404)
