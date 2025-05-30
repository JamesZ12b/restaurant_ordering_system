# qrcode_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Table, MenuItem,Floor,Order
import os
import qrcode
import stripe
import json
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


stripe.api_key = settings.STRIPE_SECRET_KEY

def generate_qr_code(table_number):
    # 确保 qr_codes 目录存在
    qr_code_dir = 'media/qr_codes'
    if not os.path.exists(qr_code_dir):
        os.makedirs(qr_code_dir)

    # 生成二维码
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"http://114.55.113.74:8000/table/menu/{table_number}/")  # 假设这是餐桌的链接
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
    try:
        table = Table.objects.get(table_number=table_number)
        menu_items = MenuItem.objects.all()
        context = {
            'table_number': table_number,
            'menu_items': menu_items,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY
        }
        return render(request, 'qrcode_app/menu.html', context)
    except Table.DoesNotExist:
        return redirect('table_list')


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


@csrf_exempt
def create_payment_intent(request):
    try:
        data = json.loads(request.body)
        table_number = data.get('table_number')
        items = data.get('items', [])

        # Calculate total amount
        amount = sum(float(item.get('price', 0)) for item in items)

        # Create order
        table = Table.objects.get(table_number=table_number)
        order = Order.objects.create(
            table=table,
            items=items,
            total_amount=amount,
            status='pending'
        )

        # Create Stripe PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency='usd',
            metadata={
                'order_id': order.id,
                'table_number': table_number
            }
        )

        # Update order with payment intent ID
        order.stripe_payment_intent = intent.id
        order.save()

        return JsonResponse({
            'clientSecret': intent.client_secret,
            'order_id': order.id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': str(e)}, status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata']['order_id']

        try:
            order = Order.objects.get(id=order_id)
            order.status = 'paid'
            order.save()
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)

    return JsonResponse({'status': 'success'})


@csrf_exempt
def payment_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        return JsonResponse({
            'status': order.status,
            'message': f'Order is {order.status}'
        })
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

def kitchen_order_view(request):
    orders = Order.objects.filter(status='pending')  # 或使用其他条件
    context = {
        'orders': orders
    }
    return render(request, 'qrcode_app/kitchen_order_display.html', context)


@csrf_exempt
def submit_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        items = data.get('items', [])
        table_number = data.get('table_number')

        # 创建订单
        table = get_object_or_404(Table, table_number=table_number)

        # 创建实际订单时，确保设置初始状态和其他必要字段
        order = Order.objects.create(
            table=table,
            total_amount=sum(item['price'] * item['quantity'] for item in items),  # 计算总金额
            status='pending'  # 初始状态设为 pending
        )

        for item in items:
            # 假设您有一个 MenuItem 模型来存储菜单项信息
            menu_item = MenuItem.objects.get(id=item['id'])  # 假设传递的是菜单项 ID
            order.items.create(menu_item=menu_item, quantity=item['quantity'])

        order.save()

        return JsonResponse({'success': True, 'order_id': order.id})  # 返回成功和订单 ID
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@csrf_exempt
def mark_all_orders_done(request, table_number):
    """
    将某桌(table_number)下所有未完成的订单置为 `completed` 状态
    """
    if request.method == 'POST':
        from .models import Order
        orders = Order.objects.filter(table__table_number=table_number, status__in=['pending','preparing'])
        orders.update(status='completed')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

def clear_completed_orders(request):
    if request.method == 'POST':
        # 删除已完成状态的订单
        deleted_count, _ = Order.objects.filter(status='completed').delete()
        return JsonResponse({'success': True, 'deleted_count': deleted_count})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

