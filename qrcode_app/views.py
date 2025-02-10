from django.shortcuts import render
from django.http import HttpResponse
import qrcode
import cv2
import numpy as np

def generate_qr(request):
    """生成二维码并返回给用户"""
    if request.method == 'POST':
        data = request.POST.get('data')  # 从表单获取数据
        if data:
            # 生成二维码
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')

            # 将二维码图像转换为响应
            response = HttpResponse(content_type='image/png')
            img.save(response, 'PNG')
            return response
    return render(request, 'generate_qr.html')

def scan_qr(request):
    """扫描二维码并返回结果"""
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        # 使用 OpenCV 读取上传的图像
        img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector(img)

        if data:
            return HttpResponse(f'二维码内容: {data}')
        else:
            return HttpResponse('未检测到二维码')

    return render(request, 'scan_qr.html')
