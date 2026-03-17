import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_service.settings')
django.setup()

from app.models import Book

if Book.objects.count() == 0:
    books = [
        Book(title="The Great Gatsby", author="F. Scott Fitzgerald", price=10.99, stock=50),
        Book(title="1984", author="George Orwell", price=8.99, stock=100),
        Book(title="To Kill a Mockingbird", author="Harper Lee", price=12.50, stock=30),
        Book(title="Pride and Prejudice", author="Jane Austen", price=9.99, stock=40),
        Book(title="Moby-Dick", author="Herman Melville", price=15.00, stock=20),
        Book(title="War and Peace", author="Leo Tolstoy", price=20.00, stock=10),
        Book(title="The Catcher in the Rye", author="J.D. Salinger", price=11.20, stock=60),
        Book(title="The Hobbit", author="J.R.R. Tolkien", price=14.99, stock=80),
        Book(title="Crime and Punishment", author="Fyodor Dostoevsky", price=13.50, stock=25),
        Book(title="The Odyssey", author="Homer", price=16.99, stock=15),
        Book(title="Brave New World", author="Aldous Huxley", price=10.50, stock=45),
        Book(title="Jane Eyre", author="Charlotte Brontë", price=9.50, stock=55),
    ]
    Book.objects.bulk_create(books)
    print("Inserted 12 dummy books for pagination demonstration.")
else:
    print("Books already exist in the database.")
