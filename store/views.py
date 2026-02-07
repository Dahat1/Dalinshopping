from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import OrderForm, RegisterForm, ProfileUpdateForm, CancelOrderForm
from .models import Order, OrderItem, Product, Profile, OrderScreenshot
from decimal import Decimal

# --- AYARLAR ---
MARKET_RATE = 1450      
OUR_RATE = 1200           
SHIPPING_FEE = 5000       
POINT_EARN_RATE = 1000    
POINT_VALUE_IQD = 25   

# --- ANA SAYFA ---
def home(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'store/index.html', {'products': products})

# --- SİPARİŞ OLUŞTURMA (DRAFT) ---
@login_required
def create_order(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    missing_profile = not profile.phone or not profile.address or not profile.city

    if request.method == 'POST':
        # 1. Adres Eksikse Kaydet
        if missing_profile:
            phone_input = request.POST.get('phone')
            city_input = request.POST.get('city')
            address_input = request.POST.get('address')
            
            if not phone_input or not city_input or not address_input:
                messages.error(request, '⚠️ Please fill in all delivery details.')
                return redirect('create_order')
            
            profile.phone = phone_input
            profile.city = city_input
            profile.address = address_input
            profile.save()

        # 2. Linkleri ve Fiyatları Al
        links = request.POST.getlist('links[]')
        prices = request.POST.getlist('prices[]')
        use_points = request.POST.get('use_points') == 'on'
        images = request.FILES.getlist('screenshots')

        if not links or not prices:
            messages.error(request, 'Please add at least one item.')
            return redirect('create_order')

        # Siparişi Oluştur
        order = Order.objects.create(
            user=request.user,
            status='draft',
            wants_to_use_points=use_points
        )
        
        for img in images:
            OrderScreenshot.objects.create(order=order, image=img)
        
        # Ürünleri Kaydet
        for link, price in zip(links, prices):
            if link and price:
                OrderItem.objects.create(
                    order=order,
                    product_link=link,
                    manual_price_usd=Decimal(price)
                )

        return redirect('order_preview', order_id=order.id)

    return render(request, 'store/create_order.html', {
        'profile': profile,
        'point_value': POINT_VALUE_IQD,
        'missing_profile': missing_profile
    })

# --- SİPARİŞ DÜZENLEME ---
@login_required
def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status='draft')
    
    if request.method == 'POST':
        links = request.POST.getlist('links[]')
        prices = request.POST.getlist('prices[]')
        use_points = request.POST.get('use_points') == 'on'
        new_images = request.FILES.getlist('screenshots')

        if not links or not prices:
            messages.error(request, 'Please add at least one item.')
            return redirect('edit_order', order_id=order.id)

        # Eski ürünleri sil (Temiz sayfa)
        order.items.all().delete()

        # Yeni ürünleri ekle
        for link, price in zip(links, prices):
            if link and price:
                OrderItem.objects.create(
                    order=order,
                    product_link=link,
                    manual_price_usd=Decimal(price)
                )

        order.wants_to_use_points = use_points
        order.save()

        if new_images:
            for img in new_images:
                OrderScreenshot.objects.create(order=order, image=img)

        return redirect('order_preview', order_id=order.id)
    
    return render(request, 'store/create_order.html', {
        'profile': request.user.profile,
        'point_value': POINT_VALUE_IQD,
        'editing': True,
        'order': order
    })

# --- ÖNİZLEME (STEP 2: REVIEW) - DÜZELTİLDİ ---
@login_required
def order_preview(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status='draft')
    profile = request.user.profile
    
    # Toggle Points Butonu
    if request.method == 'POST' and 'toggle_points' in request.POST:
        order.wants_to_use_points = not order.wants_to_use_points
        order.save()
        return redirect('order_preview', order_id=order.id)

    # --- KRİTİK DÜZELTME BURADA ---
    items = order.items.all() # Tüm ürünleri çek
    
    # Tüm ürünlerin fiyatını topla (SUM)
    total_usd = sum(item.manual_price_usd for item in items) 

    # Hesaplamaları TOPLAM USD üzerinden yap
    market_price_iqd = (total_usd * Decimal(MARKET_RATE))
    our_price_iqd = (total_usd * Decimal(OUR_RATE))
    shipping_fee = Decimal(SHIPPING_FEE)
    
    total_before_discount = our_price_iqd + shipping_fee
    
    discount = 0
    points_to_spend = 0

    if order.wants_to_use_points and profile.dalin_points > 0:
        points_to_spend = profile.dalin_points
        discount = points_to_spend * POINT_VALUE_IQD
        if discount > total_before_discount:
            points_to_spend = int(total_before_discount / POINT_VALUE_IQD)
            discount = points_to_spend * POINT_VALUE_IQD
            
    final_price = total_before_discount - discount

    return render(request, 'store/order_preview.html', {
        'order': order,
        'items': items,
        'market_rate': MARKET_RATE,
        'our_rate': OUR_RATE,
        'market_price_iqd': market_price_iqd,
        'our_price_iqd': our_price_iqd,
        'shipping_fee': shipping_fee,
        'discount': discount,
        'final_price': final_price,
        'points_to_spend': points_to_spend,
        'profile': profile,
        'screenshots': order.screenshots.all()
    })

# --- ONAYLA (STEP 3: SUCCESS) - DÜZELTİLDİ ---
@login_required
def confirm_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status='draft')
    
    if request.method == 'POST':
        profile = request.user.profile
        
        # --- KRİTİK DÜZELTME BURADA DA YAPILDI ---
        items = order.items.all()
        total_usd = sum(item.manual_price_usd for item in items)

        our_price_iqd = (total_usd * Decimal(OUR_RATE))
        total_before_discount = our_price_iqd + Decimal(SHIPPING_FEE)
        
        discount = 0
        points_spent = 0
        
        if order.wants_to_use_points and profile.dalin_points > 0:
            points_spent = profile.dalin_points
            discount = points_spent * POINT_VALUE_IQD
            if discount > total_before_discount:
                points_spent = int(total_before_discount / POINT_VALUE_IQD)
                discount = points_spent * POINT_VALUE_IQD
            
            profile.dalin_points -= points_spent
            profile.save()
            
        final_price = total_before_discount - discount
        points_to_earn = int(final_price / POINT_EARN_RATE)
        
        # Kaydet
        order.total_price_iqd = final_price
        order.points_spent = points_spent
        order.discount_amount = discount
        order.points_to_earn = points_to_earn
        order.status = 'pending'
        order.save()
        
        messages.success(request, '🎉 Order Confirmed!')
        return render(request, 'store/order_success.html', {'order': order})
        
    return redirect('home')

# --- DİĞERLERİ (AYNI) ---
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).exclude(status='draft').order_by('-created_at')
    return render(request, 'store/my_orders.html', {'orders': orders})

@login_required
def order_success(request):
    return render(request, 'store/order_success.html')

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status != 'pending':
        messages.error(request, '❌ Cannot cancel.')
        return redirect('my_orders')
    
    if request.method == 'POST':
        form = CancelOrderForm(request.POST)
        if form.is_valid():
            order.status = 'cancel_requested'
            order.cancel_reason = form.cleaned_data['reason']
            order.save()
            messages.info(request, '📩 Request sent.')
            return redirect('my_orders')
    else:
        form = CancelOrderForm()
    return render(request, 'store/cancel_request.html', {'form': form, 'order': order})

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Profile updated!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'store/profile.html', {'form': form, 'profile': profile})

def faq_view(request):
    return render(request, 'store/faq.html')

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')