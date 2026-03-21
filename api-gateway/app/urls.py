from django.urls import path
from .views import dashboard, book_detail, login_page, register_page, view_books, add_book, cart_page, checkout_page, shipping_page, shipping_list_page, staff_list_page, customer_list_page

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

    # ── Customer Service UI (Proxied from 8003 to 8000) ─────────────────────
    path('customer/login/',    login_page,    {'template': 'customer_login.html'},    name='customer_login_ui'),
    path('customer/register/', register_page, {'template': 'customer_register.html'}, name='customer_register_ui'),
    path('customer/dashboard/', dashboard,    {'template': 'customer_dashboard.html'}, name='customer_dashboard_ui'),
    path('customer/view-books/', view_books,  {'template': 'customer_view_books.html'}, name='customer_view_books_ui'),
    path('customer/cart/',       cart_page,   {'template': 'customer_cart.html'},       name='customer_cart_ui'),
    path('customer/books/<int:book_id>/', book_detail, {'template': 'customer_book_detail.html'}, name='customer_book_detail'),
    path('customer/checkout/', checkout_page, {'template': 'customer_checkout.html'}, name='customer_checkout'),
    path('customer/shipping/', shipping_page, {'template': 'customer_shipping.html'}, name='customer_shipping'),
    path('customer/shipping-list/', shipping_list_page, {'template': 'customer_shipping_list.html'}, name='customer_shipping_ui'),

    # ── Staff Service UI ────────────────────────────────────────────────────
    path('staff/login/',    login_page,    {'template': 'staff_login.html'},    name='staff_login_ui'),
    path('staff/register/', register_page, {'template': 'staff_register.html'}, name='staff_register_ui'),
    path('staff/dashboard/', dashboard,    {'template': 'staff_dashboard.html'}, name='staff_dashboard_ui'),
    path('staff/view-books/', view_books,  {'template': 'staff_view_books.html'}, name='staff_view_books_ui'),
    path('staff/add-book/',  add_book,     {'template': 'staff_add_book.html'},  name='staff_add_book_ui'),
    path('staff/books/<int:book_id>/', book_detail, {'template': 'staff_book_detail.html'}, name='staff_book_detail'),
    path('staff/shipping-list/', shipping_list_page, {'template': 'staff_shipping_list.html'}, name='staff_shipping_ui'),
    
    # ── Manager Service UI ───────────────────────────────────────────────────
    path('manager/login/',     login_page,    {'template': 'manager_login.html'},    name='manager_login_ui'),
    path('manager/register/',  register_page, {'template': 'manager_register.html'}, name='manager_register_ui'),
    path('manager/dashboard/', dashboard,     {'template': 'manager_dashboard.html'}, name='manager_dashboard_ui'),
    path('manager/view-books/', view_books,   {'template': 'manager_view_books.html'}, name='manager_view_books_ui'),
    path('manager/books/<int:book_id>/', book_detail, {'template': 'manager_book_detail.html'}, name='manager_book_detail_ui'),
    path('manager/staff/',     staff_list_page, {'template': 'manager_staff_list.html'}, name='manager_staff_list_ui'),
    path('manager/customers/', customer_list_page, {'template': 'manager_customer_list.html'}, name='manager_customer_list_ui'),
]
