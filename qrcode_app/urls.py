# qrcode_app/urls.py

from django.urls import path
from .views import create_table, view_qr_code

urlpatterns = [
    path('create/', create_table, name='create_table'),
    path('qr_code/<str:table_number>/', view_qr_code, name='view_qr_code'),  # 确保这个路由存在
]