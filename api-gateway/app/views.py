from django.shortcuts import render


def _no_cache_render(request, template, context=None):
    """Render a template with no-cache headers to prevent browser caching stale JS."""
    response = render(request, template, context or {})
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


def dashboard(request, template="dashboard.html"):
    return _no_cache_render(request, template)

def book_detail(request, book_id, template="book_detail.html"):
    return _no_cache_render(request, template, {"book_id": book_id})

def login_page(request, template="login.html"):
    return _no_cache_render(request, template)

def register_page(request, template="register.html"):
    return _no_cache_render(request, template)

def view_books(request, template="view_books.html"):
    return _no_cache_render(request, template)

def add_book(request, template="add_book.html"):
    return _no_cache_render(request, template)

def cart_page(request, template="cart.html"):
    return _no_cache_render(request, template)

def checkout_page(request, template="checkout.html"):
    return _no_cache_render(request, template)

def shipping_page(request, template="shipping.html"):
    return _no_cache_render(request, template)

def shipping_list_page(request, template="shipping_list.html"):
    return _no_cache_render(request, template)

def staff_list_page(request, template="staff_list.html"):
    return _no_cache_render(request, template)

def customer_list_page(request, template="customer_list.html"):
    return _no_cache_render(request, template)

def favorites_page(request, template="customer_favorites.html"):
    return _no_cache_render(request, template)
