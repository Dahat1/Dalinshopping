from django.contrib import admin
from django.utils.html import format_html
from .models import Profile, Order, OrderItem, Product, OrderScreenshot

# --- 1. SİPARİŞ İÇİNDEKİ LİNKLER ---
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    verbose_name = "Product Link"
    verbose_name_plural = "Product Links"
    readonly_fields = ('product_link', 'manual_price_usd')

# --- 2. SİPARİŞ RESİMLERİ ---
class OrderScreenshotInline(admin.TabularInline):
    model = OrderScreenshot
    extra = 0
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<a href="{}" target="_blank"><img src="{}" style="max-height: 100px; border-radius: 5px;" /></a>', obj.image.url, obj.image.url)
        return ""
    image_preview.short_description = "Preview"

# --- 3. SİPARİŞ YÖNETİMİ ---
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # LİSTEDE GÖRÜNECEKLER (actual_cost_usd EKLENDİ)
    list_display = ('id', 'user', 'customer_phone', 'total_price_iqd', 'status_colored', 'actual_cost_usd', 'created_at')
    
    # LİSTEDEN DÜZENLENEBİLECEKLER (status ve actual_cost_usd)
    list_editable = ('actual_cost_usd',)
    
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__profile__phone')
    inlines = [OrderItemInline, OrderScreenshotInline]
    readonly_fields = ('customer_info', 'cancel_reason')
    
    fieldsets = (
        ('Order Info', {
            # actual_cost_usd BURAYA DA EKLENDİ
            'fields': ('user', 'status', 'total_price_iqd', 'actual_cost_usd', 'tracking_note', 'cancel_reason')
        }),
        ('Customer Details', {
            'fields': ('customer_info',)
        }),
    )

    def customer_phone(self, obj):
        return obj.user.profile.phone
    customer_phone.short_description = "Phone"

    def status_colored(self, obj):
        color = 'black'
        if obj.status == 'pending': color = 'orange'
        elif obj.status == 'approved': color = 'blue'
        elif obj.status == 'cancel_requested': color = 'red'
        elif obj.status == 'cancelled': color = 'gray'
        elif obj.status == 'delivered': color = 'green'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = "Status"

    def customer_info(self, obj):
        profile = obj.user.profile
        return format_html(
            """
            <div style="line-height: 1.6;">
                <strong>Name:</strong> {} {} <br>
                <strong>Phone:</strong> {} <br>
                <strong>City:</strong> {} <br>
                <strong>Address:</strong> {} <br>
                <strong>Points:</strong> 💎 {}
            </div>
            """,
            obj.user.first_name, obj.user.last_name,
            profile.phone,
            profile.city,
            profile.address,
            profile.dalin_points
        )
    customer_info.short_description = "Delivery Details"

# --- DİĞERLERİ ---
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'dalin_points')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_usd', 'is_active')
    list_editable = ('is_active',)