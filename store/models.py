from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import pre_save # pre_save eklemeyi unutma

# --- 1. PROFILE ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone Number")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="City")
    address = models.TextField(blank=True, null=True, verbose_name="Full Address")
    dalin_points = models.IntegerField(default=0, verbose_name="Dalin Points")
    
    def __str__(self):
        return f"{self.user.username} - {self.dalin_points} Pts"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

# --- 2. ORDER ---
class Order(models.Model):
    STATUS_CHOICES = (
        ('draft', '📝 Draft (Not Confirmed)'),
        ('pending', '⏳ Pending Approval'),
        ('approved', '✅ Order Placed (Shein)'),
        ('dubai', '🇦🇪 Arrived in Dubai'),
        ('shipping', '🚚 On the way to Iraq'),
        ('arrived', '🏢 In Erbil Branch'),
        ('delivered', '📦 Delivered'),
        ('cancel_requested', '⚠️ Cancellation Requested'),
        ('cancelled', '❌ Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Customer")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date")
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Status")
    tracking_note = models.TextField(blank=True, null=True, verbose_name="Tracking Note")
    cancel_reason = models.TextField(blank=True, null=True, verbose_name="Cancellation Reason")

    # Fiyatlar
    total_price_iqd = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Final Price (IQD)")
    
    # --- YENİ EKLENEN ALAN: GERÇEK MALİYET (NET KÂR İÇİN) ---
    actual_cost_usd = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Real Cost ($)",
        help_text="Shein'e kupon sonrası ödenen gerçek tutar."
    )

    # Puan Sistemi
    wants_to_use_points = models.BooleanField(default=False)
    points_spent = models.IntegerField(default=0, verbose_name="Points Used")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name="Discount Amount (IQD)")
    points_to_earn = models.IntegerField(default=0, verbose_name="Points to Earn")
    points_added_to_profile = models.BooleanField(default=False, verbose_name="Points Loaded?")

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

@receiver(post_save, sender=Order)
def add_points_on_delivery(sender, instance, **kwargs):
    if instance.status == 'delivered' and not instance.points_added_to_profile:
        profile = instance.user.profile
        profile.dalin_points += instance.points_to_earn
        profile.save()
        instance.points_added_to_profile = True
        instance.save()

# --- 3. ORDER SCREENSHOTS ---
class OrderScreenshot(models.Model):
    order = models.ForeignKey(Order, related_name='screenshots', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='screenshots/')
    
    def __str__(self):
        return f"Screenshot for Order #{self.order.id}"

# --- 4. ORDER ITEMS ---
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_link = models.URLField(max_length=1000, verbose_name="Shein Link")
    manual_price_usd = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Price ($)")
    
    def __str__(self):
        return f"Link: {self.product_link[:30]}..."

# --- 5. PRODUCTS ---
class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name="Product Name")
    image = models.ImageField(upload_to='products/', verbose_name="Product Image")
    price_usd = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Price ($)")
    shein_link = models.URLField(max_length=1000, verbose_name="Shein Link")
    is_active = models.BooleanField(default=True, verbose_name="Show on Homepage?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# --- OTOMATİK E-POSTA BİLDİRİM SİSTEMİ ---
@receiver(pre_save, sender=Order)
def send_email_on_status_change(sender, instance, **kwargs):
    # Eğer sipariş yeni oluşturuluyorsa (henüz ID'si yoksa) işlem yapma
    if not instance.pk:
        return
    
    try:
        # Veritabanındaki eski halini bul
        old_order = Order.objects.get(pk=instance.pk)
        
        # Eğer durum değişmişse (Örn: pending -> approved)
        if old_order.status != instance.status:
            
            subject = f"📦 Update on Order #{instance.id}"
            message = f"""
            Hello {instance.user.username},

            Good news! The status of your order #{instance.id} has changed.
            
            🆕 New Status: {instance.get_status_display()}
            
            {f'Tracking Note: {instance.tracking_note}' if instance.tracking_note else ''}

            You can check the details on your profile:
            http://127.0.0.1:8000/my-orders/

            Thank you for shopping with Dalin Shopping!
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.user.email], # Müşterinin mailine gönder
                fail_silently=False,
            )
            print(f"📧 EMAIL SENT TO {instance.user.email}: Status changed to {instance.status}")
            
    except Order.DoesNotExist:
        pass

