from django.urls import path
from .views import CreateShipping, GetShippingDetails, GetAllShipping, DeleteShipping

urlpatterns = [
    path('shipping/', CreateShipping.as_view(), name='create-shipping'),
    path('shipping/all/', GetAllShipping.as_view(), name='get-all-shipping'),
    path('shipping/<int:order_id>/', GetShippingDetails.as_view(), name='get-shipping'),
    path('shipping/delete/<int:pk>/', DeleteShipping.as_view(), name='delete-shipping'),
]
