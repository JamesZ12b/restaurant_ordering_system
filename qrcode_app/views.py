# qrcode_app/views.py

import os
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from .models import Table, MenuItem,Floor
import qrcode

def generate_qr_code(table_number):
    # 确保 qr_codes 目录存在
    qr_code_dir = 'media/qr_codes'
    if not os.path.exists(qr_code_dir):
        os.makedirs(qr_code_dir)

    # 生成二维码
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"http://localhost:8000/table/menu/{table_number}/")  # 假设这是餐桌的链接
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

        # 创建新的餐桌实例
        table = Table(table_number=table_number)
        table.save()

        # 生成二维码并保存
        qr_code_path = generate_qr_code(table_number)
        with open(qr_code_path, 'rb') as qr_file:
            table.qr_code.save(f"table_{table_number}.png", ContentFile(qr_file.read()))
        table.save()

        # 成功创建后重定向到创建餐桌页面，并传递餐桌编号
        return render(request, 'qrcode_app/create_table.html', {
            'table_number': table_number
        })
    return render(request, 'qrcode_app/create_table.html')

def view_qr_code(request, table_number):
    # 根据餐桌编号获取餐桌对象
    table = get_object_or_404(Table, table_number=table_number)
    return render(request, 'qrcode_app/view_qr_code.html', {'table': table})

def table_list(request):
    tables = Table.objects.all()  # 获取所有餐桌
    return render(request, 'qrcode_app/table_list.html', {'tables': tables})

# qrcode_app/views.py

def menu_view(request, table_number):
    # 获取所有菜单项
    menu_items = MenuItem.objects.all()
    return render(request, 'qrcode_app/menu.html', {
        'table_number': table_number,
        'menu_items': menu_items
    })

def floor_layout(request):
    """
    返回楼层和桌位布局到前端页面。
    如果你要渲染上一次发给你的 floor_layout.html，就在这里 render('floor_layout.html', {...})
    """
    floors = Floor.objects.all()
    tables = Table.objects.select_related('floor').all()
    return render(request, 'qrcode_app/floor_layout.html', {
        'floors': floors,
        'tables': tables
    })

def combined_view(request):
    floors = Floor.objects.all()
    tables = Table.objects.all()
    return render(request, 'qrcode_app/combined_page.html', {
        'floors': floors,
        'tables': tables,
    })


def table_list_view(request):
    all_tables = Table.objects.all().order_by('table_number')

    # 获取所有楼层
    floors = Floor.objects.all().order_by('id')

    # 构造前端可用的结构，如 floorData = { 楼层ID: [ {id, seats, ...}, ...], ...}
    floor_data = {}
    for floor in floors:
        # 查找该楼层下所有桌子
        tables = floor.tables.all().order_by('table_number')
        floor_data[floor.id] = [
            {
                "id": str(t.table_number),  # 改为字符串，方便前端识别
                "seats": t.seating_capacity if hasattr(t, 'seating_capacity') else 4,
                "status": "available"  # 初始值，你可根据数据库中的某个状态字段来决定
            }
            for t in tables
        ]

    return render(request, 'table_list.html', {
        "floor_data_json": floor_data,
        'tables': all_tables,  # 如果需要在模板中使用所有桌子
    })