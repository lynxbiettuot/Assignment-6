from django.contrib import admin
from django.urls import path, include
from app.views import recommend

urlpatterns = [
    path('admin/', admin.site.urls),
    path('recommend/<int:user_id>/', recommend, name='recommend'),
]
