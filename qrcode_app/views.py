# qrcode_app/views.py

import os
import qrcode
import stripe
import json
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Table, MenuItem, Order

# Initialize Stripe with test key
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_table(request):
    if request.method == 'POST':
        table_number = request.POST.get('table_number')
        if table_number:
            # Check if table already exists
            if Table.objects.filter(table_number=table_number).exists():
                # You might want to add an error message here
                return redirect('table_list')
            
            table = Table.objects.create(table_number=table_number)
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(request.build_absolute_uri(f'/table/menu/{table_number}/'))
            qr.make(fit=True)
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Save QR code
            blob = ContentFile(b'')
            qr_image.save(blob, 'PNG')
            table.qr_code.save(f'table_{table_number}.png', blob)
            
            return redirect('view_qr_code', table_number=table_number)
    return render(request, 'qrcode_app/create_table.html')

def view_qr_code(request, table_number):
    try:
        table = Table.objects.get(table_number=table_number)
        return render(request, 'qrcode_app/view_qr_code.html', {'table': table})
    except Table.DoesNotExist:
        return redirect('table_list')

def table_list(request):
    tables = Table.objects.all()
    return render(request, 'qrcode_app/table_list.html', {'tables': tables})

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
