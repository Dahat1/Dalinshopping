"""
Dalin Shopping URL Configuration
Updated for Multi-Language Support (I18N)
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns # <-- BU ÇOK ÖNEMLİ
from django.contrib.auth import views as auth_views

from store.views import (
    home, create_order, order_preview, confirm_order, edit_order,
    order_success, my_orders, cancel_order, profile_view, 
    register_view, login_view, logout_view, faq_view
)

# 1. Dil Değiştirme Fonksiyonu (Navbar'daki butonlar için şart)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

# 2. Bütün Sayfaları Dil Desteği İçine Alıyoruz (i18n_patterns)
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    
    # Sipariş İşlemleri
    path('new-order/', create_order, name='create_order'),
    path('edit-order/<int:order_id>/', edit_order, name='edit_order'),
    path('preview/<int:order_id>/', order_preview, name='order_preview'),
    path('confirm/<int:order_id>/', confirm_order, name='confirm_order'),
    path('order-success/', order_success, name='order_success'),
    
    # Kullanıcı Sayfaları
    path('my-orders/', my_orders, name='my_orders'),
    path('cancel-order/<int:order_id>/', cancel_order, name='cancel_order'),
    path('profile/', profile_view, name='profile'),
    
    # Auth (Giriş/Kayıt)
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # SSS
    path('faq/', faq_view, name='faq'),

    # --- ŞİFRE SIFIRLAMA (PASSWORD RESET) ---
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html"), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), name="password_reset_complete"),
    
    # Eğer "prefix_default_language=False" yaparsan, İngilizce'de /en/ yazmaz.
    # Şu an varsayılan ayarda bıraktım, her dilde kod görünecek (Örn: /en/new-order, /ar/new-order).
)

# Medya Dosyaları (Resimler) için
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)