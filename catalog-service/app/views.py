from django.shortcuts import render
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.conf import settings

# Create your views here.

# Since book-service is in the same docker-compose network, we use its service name
BOOK_SERVICE_URL = "http://book-service:8000/books/"


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CatalogListView(APIView):
    """
    Fetches the full list of books from book-service, paginates them,
    and returns them to the client. Supporting search and sorting.
    """
    def get(self, request):
        try:
            # Get search and sort parameters from query string
            search_query = request.query_params.get('search', '').lower()
            sort_by = request.query_params.get('sort', '')

            # Fetch ALL books from book service
            response = requests.get(BOOK_SERVICE_URL)
            
            if response.status_code != 200:
                return Response(
                    {"error": f"Failed to fetch books from Book Service. Status: {response.status_code}"}, 
                    status=502
                )
            
            books_data = response.json()
            
            # Apply search filter
            if search_query:
                books_data = [
                    book for book in books_data 
                    if search_query in book.get('title', '').lower() or 
                       search_query in book.get('author', '').lower()
                ]

            # Apply sorting
            if sort_by == 'title_asc':
                books_data.sort(key=lambda x: x.get('title', '').lower())
            elif sort_by == 'title_desc':
                books_data.sort(key=lambda x: x.get('title', '').lower(), reverse=True)
            elif sort_by == 'price_asc':
                books_data.sort(key=lambda x: float(x.get('price', 0)))
            elif sort_by == 'price_desc':
                books_data.sort(key=lambda x: float(x.get('price', 0)), reverse=True)
            
            import sys
            page_num = request.query_params.get('page', '1')
            sys.stderr.write(f"\n[CATALOG DEBUG] Processing request: page={page_num}, total_items={len(books_data)}\n")
            sys.stderr.flush()

            # Paginate the filtered and sorted data
            paginator = StandardResultsSetPagination()
            try:
                paginated_data = paginator.paginate_queryset(books_data, request)
                return paginator.get_paginated_response(paginated_data)
            except Exception as paginate_err:
                sys.stderr.write(f"[CATALOG ERROR] Pagination failed: {str(paginate_err)}\n")
                sys.stderr.flush()
                # Fallback to returning all if pagination fails (not ideal but avoids 500)
                return Response({
                    "count": len(books_data),
                    "next": None,
                    "previous": None,
                    "results": books_data[:10]
                })
            
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Error connecting to Book Service: {str(e)}"}, status=503)


class CatalogDetailView(APIView):
    """
    Fetches details for a single book from book-service.
    """
    def get(self, request, pk):
        try:
            response = requests.get(f"{BOOK_SERVICE_URL}{pk}/")
            
            if response.status_code == 404:
                return Response({"error": "Book not found"}, status=404)
            elif response.status_code != 200:
                return Response(
                    {"error": f"Failed to fetch book detail from Book Service. Status: {response.status_code}"}, 
                    status=502
                )
            
            return Response(response.json())
            
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Error connecting to Book Service: {str(e)}"}, status=503)
