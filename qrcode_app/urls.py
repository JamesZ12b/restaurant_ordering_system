# qrcode_app/urls.py

from django.urls import path
from .views import create_table, view_qr_code, table_list

urlpatterns = [
    path('', table_list, name='table_list'),  # 餐桌列表
    path('create/', create_table, name='create_table'),  # 创建餐桌
    path('qr_code/<str:table_number>/', view_qr_code, name='qr_code_view'),  # 餐桌二维码视图
]