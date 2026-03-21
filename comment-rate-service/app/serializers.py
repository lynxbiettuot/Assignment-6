from rest_framework import serializers
from .models import CommentRate

class CommentRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentRate
        fields = ['id', 'book_id', 'user_id', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']
