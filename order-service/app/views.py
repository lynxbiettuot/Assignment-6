from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
import requests

CART_SERVICE_URL = "http://cart-service:8000"

class CreateOrderFromCart(APIView):
    def post(self, request):
        customer_id = request.data.get("customer_id")
        cart_id = request.data.get("cart_id")

        if not customer_id or not cart_id:
            return Response({"error": "customer_id and cart_id required"}, status=400)

        # 1. Fetch Cart from Cart Service
        try:
            r = requests.get(f"{CART_SERVICE_URL}/carts/{customer_id}/")
            if r.status_code != 200 or "error" in r.json():
                return Response({"error": "Cart is empty or not found"}, status=400)
            cart_items = r.json()
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Failed to connect to cart service: {e}"}, status=500)

        if not cart_items:
            return Response({"error": "Cart is empty"}, status=400)

        # 2. Calculate Total Price and check inventory (simulated check here for brevity)
        # Ideally, we query book-service to get current prices and stock.
        # But since cart-service didn't explicitly return prices, we must fetch them from book-service.
        BOOK_SERVICE_URL = "http://book-service:8000"
        try:
            r_books = requests.get(f"{BOOK_SERVICE_URL}/books/")
            if r_books.status_code != 200:
                return Response({"error": "Failed to fetch book prices"}, status=500)
            all_books = r_books.json()
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Failed to connect to book service: {e}"}, status=500)

        total_price = 0
        order_items_data = []

        for item in cart_items:
            book_id = item['book_id']
            qty = item['quantity']
            book_details = next((b for b in all_books if b['id'] == book_id), None)
            
            if not book_details:
                return Response({"error": f"Book ID {book_id} not found"}, status=400)
            
            price = float(book_details['price'])
            total_price += price * qty
            
            order_items_data.append({
                "book_id": book_id,
                "quantity": qty,
                "price": price
            })

        # 3. Create the Order (Pending)
        order = Order.objects.create(
            customer_id=customer_id,
            total_price=total_price,
            status="Pending"
        )

        # 4. Create the Order Items
        for item_data in order_items_data:
            OrderItem.objects.create(
                order=order,
                book_id=item_data["book_id"],
                quantity=item_data["quantity"],
                price=item_data["price"]
            )

        # Cart clearance will now happen on frontend after payment processing.

        
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=201)

class GetOrders(APIView):
    def get(self, request, customer_id):
        orders = Order.objects.filter(customer_id=customer_id)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class GetOrderById(APIView):
    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

class GetAllOrders(APIView):
    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
