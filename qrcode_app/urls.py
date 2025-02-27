# qrcode_app/urls.py

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    create_table, 
    view_qr_code, 
    table_list, 
    menu_view,
    create_payment_intent,
    webhook,
    payment_status
)

urlpatterns = [
    path('', table_list, name='table_list'),  # /table/
    path('create/', create_table, name='create_table'),  # /table/create/
    path('<str:table_number>/', view_qr_code, name='view_qr_code'),  # /table/1/
    path('menu/<str:table_number>/', menu_view, name='menu'),  # /table/menu/1/
    path('api/create-payment-intent/', create_payment_intent, name='create_payment_intent'),
    path('api/webhook/', webhook, name='webhook'),
    path('api/payment-status/<int:order_id>/', payment_status, name='payment_status'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
