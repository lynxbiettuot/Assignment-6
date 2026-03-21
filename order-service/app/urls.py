from django.urls import path
from .views import CreateOrderFromCart, GetOrders, GetOrderById, GetAllOrders

urlpatterns = [
    path('orders/', CreateOrderFromCart.as_view(), name='create-order'),
    path('orders/all/', GetAllOrders.as_view(), name='get-all-orders'),
    path('orders/users/<int:customer_id>/', GetOrders.as_view(), name='get-user-orders'),
    path('orders/detail/<int:pk>/', GetOrderById.as_view(), name='get-order-by-id'),
]
