from django.urls import path
from .views import generate_qr, scan_qr

urlpatterns = [
    path('generate/', generate_qr, name='generate_qr'),  # 生成二维码的 URL
    path('scan/', scan_qr, name='scan_qr'),              # 扫描二维码的 URL
]