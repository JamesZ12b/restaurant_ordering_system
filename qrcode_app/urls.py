# qrcode_app/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import create_table, view_qr_code, table_list, menu_view, create_payment_intent,webhook, payment_status

urlpatterns = [
    path('', table_list, name='table_list'),  # 餐桌列表
    path('create/', create_table, name='create_table'),  # 创建餐桌
    path('qr_code/<str:table_number>/', view_qr_code, name='qr_code_view'),
    path('menu/<str:table_number>/', menu_view, name='menu_view'),# 餐桌二维码视图
    path('api/create-payment-intent/', create_payment_intent, name='create_payment_intent'),
    path('api/webhook/', webhook, name='webhook'),
    path('api/payment-status/<int:order_id>/', payment_status, name='payment_status'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

