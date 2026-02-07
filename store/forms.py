from django import forms
from django.contrib.auth.models import User
from .models import Order, Profile

# --- 1. ÇOKLU DOSYA İÇİN ÖZEL SINIFLAR ---
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

# --- 2. FORMLAR ---

class OrderForm(forms.Form):
    product_link = forms.URLField(
        label="Shein Cart/Product Link", 
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Paste the Shein link here...'})
    )
    
    price_usd = forms.DecimalField(
        label="Total Price in Cart ($)", 
        max_digits=6, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 52.40'})
    )
    
    screenshots = MultipleFileField(
        label="Upload Cart Screenshots (Select Multiple)",
        required=False 
    )

    use_points = forms.BooleanField(
        required=False, 
        label="Use Dalin Points for Discount?",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    # --- YENİ EKLENEN ADRES ALANLARI (Opsiyonel) ---
    # Sadece profili eksik olanlardan isteyeceğiz
    phone = forms.CharField(
        required=False, 
        label="Phone Number",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0750 XXX XX XX'})
    )
    city = forms.CharField(
        required=False, 
        label="City",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Erbil'})
    )
    address = forms.CharField(
        required=False, 
        label="Full Address",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Street, Building, Near landmark...'})
    )

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}), label="Password")
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}), label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match!")

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'city', 'address']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CancelOrderForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Reason"
    )