from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Shipping
from .serializers import ShippingSerializer

class CreateShipping(APIView):
    def post(self, request):
        serializer = ShippingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class GetShippingDetails(APIView):
    def get(self, request, order_id):
        try:
            shipping = Shipping.objects.get(order_id=order_id)
            serializer = ShippingSerializer(shipping)
            return Response(serializer.data)
        except Shipping.DoesNotExist:
            return Response({"error": "Shipping details not found"}, status=404)

class GetAllShipping(APIView):
    def get(self, request):
        shippings = Shipping.objects.all()
        serializer = ShippingSerializer(shippings, many=True)
        return Response(serializer.data)

class DeleteShipping(APIView):
    def delete(self, request, pk):
        try:
            shipping = Shipping.objects.get(pk=pk)
            shipping.delete()
            return Response(status=204)
        except Shipping.DoesNotExist:
            return Response({"error": "Shipping not found"}, status=404)
