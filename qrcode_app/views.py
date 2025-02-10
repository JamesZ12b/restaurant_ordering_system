# qrcode_app/views.py

import os
import qrcode
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from .models import Table


def generate_qr_code(table_number):
    # 确保 qr_codes 目录存在
    qr_code_dir = 'media/qr_codes'
    if not os.path.exists(qr_code_dir):
        os.makedirs(qr_code_dir)

        # 生成二维码
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"http://localhost:8000/table/{table_number}/")  # 假设这是餐桌的链接
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # 保存二维码到文件
    file_name = os.path.join(qr_code_dir, f"table_{table_number}.png")
    img.save(file_name)

    return file_name


def create_table(request):
    if request.method == 'POST':
        table_number = request.POST.get('table_number')

        # 检查餐桌编号是否已存在
        if Table.objects.filter(table_number=table_number).exists():
            return render(request, 'qrcode_app/create_table.html', {
                'error': '该餐桌编号已存在，请使用其他编号。'
            })

        table = Table(table_number=table_number)
        table.save()

        # 生成二维码并保存
        qr_code_path = generate_qr_code(table_number)
        table.qr_code.save(f"table_{table_number}.png", ContentFile(open(qr_code_path, 'rb').read()))
        table.save()

        # 成功创建后重定向到创建餐桌页面，并传递餐桌编号
        return render(request, 'qrcode_app/create_table.html', {
            'table_number': table_number
        })
    return render(request, 'qrcode_app/create_table.html')

# qrcode_app/views.py

def view_qr_code(request, table_number):
    try:
        table = Table.objects.get(table_number=table_number)
    except Table.DoesNotExist:
        return render(request, 'qrcode_app/error.html', {'error': '餐桌不存在'})

    return render(request, 'qrcode_app/view_qr_code.html', {'table': table})

