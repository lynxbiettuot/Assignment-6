from django.db import models

class CommentRate(models.Model):
    book_id = models.IntegerField()
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=255)
    rating = models.IntegerField()  # 1 to 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user_name} rated Book {self.book_id}: {self.rating} stars"
