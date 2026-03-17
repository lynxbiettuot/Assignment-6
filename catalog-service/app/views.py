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
    and returns them to the client.
    """
    def get(self, request):
        try:
            # Fetch ALL books from book service
            # In a production app with millions of records, we would pass the pagination 
            # parameters to the book-service instead. For this assignment, we fetch all 
            # and paginate in the catalog service as requested.
            response = requests.get(BOOK_SERVICE_URL)
            
            if response.status_code != 200:
                return Response(
                    {"error": f"Failed to fetch books from Book Service. Status: {response.status_code}"}, 
                    status=502
                )
            
            books_data = response.json()
            
            # Paginate the data
            paginator = StandardResultsSetPagination()
            # We mock a queryset list for the paginator
            paginated_data = paginator.paginate_queryset(books_data, request)
            
            return paginator.get_paginated_response(paginated_data)
            
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
