from django.shortcuts import render

def dashboard(request):
    return render(request, "dashboard.html")

def book_detail(request, book_id):
    return render(request, "book_detail.html", {"book_id": book_id})

def login_page(request):
    return render(request, "login.html")

def register_page(request):
    return render(request, "register.html")

def view_books(request):
    return render(request, "view_books.html")

def add_book(request):
    return render(request, "add_book.html")

def cart_page(request):
    return render(request, "cart.html")

def checkout_page(request):
    return render(request, "checkout.html")

def shipping_page(request):
    return render(request, "shipping.html")

def shipping_list_page(request):
    return render(request, "shipping_list.html")
