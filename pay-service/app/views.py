from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer
import requests

SHIP_SERVICE_URL = "http://ship-service:8000"
ORDER_SERVICE_URL = "http://order-service:8000"

class ProcessPayment(APIView):
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save()
            order_id = payment.order_id
            address = request.data.get("address", "Unknown Address")
            
            # 1. Update Order Status (simulate Saga pattern step)
            # In a real app we'd call order-service to update status to "Paid"
            
            # 2. Trigger Shipping Service
            try:
                ship_res = requests.post(f"{SHIP_SERVICE_URL}/shipping/", json={
                    "order_id": order_id,
                    "address": address
                })
                if ship_res.status_code == 201:
                    return Response({"message": "Payment successful and shipping created", "payment": serializer.data}, status=201)
                else:
                    payment.status = "Failed - Shipping Error"
                    payment.save()
                    return Response({"error": "Payment succeeded but shipping failed"}, status=500)
            except requests.exceptions.RequestException as e:
                payment.status = "Failed - Network Error"
                payment.save()
                return Response({"error": f"Failed to connect to ship service: {e}"}, status=500)
                
        return Response(serializer.errors, status=400)
