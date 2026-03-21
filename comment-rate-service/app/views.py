from rest_framework import viewsets, permissions
from .models import CommentRate
from .serializers import CommentRateSerializer

class CommentRateViewSet(viewsets.ModelViewSet):
    queryset = CommentRate.objects.all().order_by('created_at')
    serializer_class = CommentRateSerializer
    permission_classes = [permissions.AllowAny] # In a real app, I'd check JWT, but here we assume the gateway/frontend handles it or passes user info

    def get_queryset(self):
        queryset = super().get_queryset()
        book_id = self.request.query_params.get('book_id')
        if book_id is not None:
            queryset = queryset.filter(book_id=book_id)
        return queryset
