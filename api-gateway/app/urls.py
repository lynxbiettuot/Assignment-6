from django.urls import path
from .views import dashboard, book_detail, login_page, register_page, view_books, add_book, cart_page, checkout_page, shipping_page, shipping_list_page

urlpatterns = [
    path('login/', login_page, name='login'),
    path('register/', register_page, name='register'),
    path('dashboard/', dashboard, name='dashboard'),
    path('view-books/', view_books, name='view_books'),
    path('add-book/', add_book, name='add_book'),
    path('cart/', cart_page, name='cart_page'),
    path('books/<int:book_id>/', book_detail, name='book_detail'),
    path('checkout/', checkout_page, name='checkout_page'),
    path('shipping/', shipping_page, name='shipping_page'),
    path('shipping-list/', shipping_list_page, name='shipping_list_page'),
]
