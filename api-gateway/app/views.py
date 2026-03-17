from django.shortcuts import render


def _no_cache_render(request, template, context=None):
    """Render a template with no-cache headers to prevent browser caching stale JS."""
    response = render(request, template, context or {})
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


def dashboard(request):
    return _no_cache_render(request, "dashboard.html")

def book_detail(request, book_id):
    return _no_cache_render(request, "book_detail.html", {"book_id": book_id})

def login_page(request):
    return _no_cache_render(request, "login.html")

def register_page(request):
    return _no_cache_render(request, "register.html")

def view_books(request):
    return _no_cache_render(request, "view_books.html")

def add_book(request):
    return _no_cache_render(request, "add_book.html")

def cart_page(request):
    return _no_cache_render(request, "cart.html")

def checkout_page(request):
    return _no_cache_render(request, "checkout.html")

def shipping_page(request):
    return _no_cache_render(request, "shipping.html")

def shipping_list_page(request):
    return _no_cache_render(request, "shipping_list.html")
