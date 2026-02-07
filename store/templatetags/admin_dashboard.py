from django import template
from django.db.models import Sum, Q
from store.models import Order, Profile, User, OrderItem
from decimal import Decimal

register = template.Library()

# SENİN PİYASADA BOZDURACAĞIN KUR (Doları kaça bozduruyorsun?)
# Bu kuru Net Kâr hesabında kullanıyoruz.
REAL_MARKET_RATE = 1450 

@register.simple_tag
def get_dashboard_stats():
    # Sadece iptal edilmemiş ve taslak olmayan siparişler
    valid_orders = Order.objects.exclude(status__in=['draft', 'cancelled', 'cancel_requested'])
    
    total_revenue_iqd = 0
    total_real_cost_iqd = 0
    
    # --- KÂR HESAPLAMA DÖNGÜSÜ ---
    for order in valid_orders:
        # Ciro (Kasaya giren IQD)
        if order.total_price_iqd:
            total_revenue_iqd += order.total_price_iqd
        
        # Maliyet Hesabı:
        # 1. Eğer sen "actual_cost_usd" (Gerçek Maliyet) girdiysen onu kullan.
        # 2. Eğer girmediysen, geçici olarak müşterinin girdiği fiyatı baz al.
        item = order.items.first()
        
        if order.actual_cost_usd:
            # Senin girdiğin indirimli tutar * Piyasa Kuru
            cost_in_iqd = order.actual_cost_usd * Decimal(REAL_MARKET_RATE)
            total_real_cost_iqd += cost_in_iqd
        elif item and item.manual_price_usd:
            # Henüz admin girmemiş, sistem varsayımı
            cost_in_iqd = item.manual_price_usd * Decimal(REAL_MARKET_RATE)
            total_real_cost_iqd += cost_in_iqd

    # NET KÂR
    real_profit = total_revenue_iqd - total_real_cost_iqd

    # --- SAYAÇLAR ---
    count_draft = Order.objects.filter(status='draft').count()
    count_pending = Order.objects.filter(status='pending').count()
    count_active = Order.objects.filter(status__in=['approved', 'dubai', 'shipping', 'arrived']).count()
    count_delivered = Order.objects.filter(status='delivered').count()
    
    # --- LİSTELER ---
    # En çok harcayan 5 müşteri
    top_customers = User.objects.annotate(
        total_spent=Sum('order__total_price_iqd', filter=Q(order__status='delivered'))
    ).order_by('-total_spent')[:5]

    # Son 5 sipariş
    recent_orders = Order.objects.exclude(status='draft').order_by('-created_at')[:5]
    
    # Puan Borcu
    points_liability = Profile.objects.aggregate(Sum('dalin_points'))['dalin_points__sum'] or 0
    
    return {
        'revenue_iqd': total_revenue_iqd,
        'net_profit': real_profit, # GERÇEK KÂR
        
        'count_draft': count_draft,
        'count_pending': count_pending,
        'count_active': count_active,
        'count_delivered': count_delivered,
        
        'top_customers': top_customers,
        'recent_orders': recent_orders,
        'points_liability': points_liability,
    }