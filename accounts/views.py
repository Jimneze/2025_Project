from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django_otp import user_has_device
from django_otp.decorators import otp_required
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
from .forms import CustomUserCreationForm, CustomAuthenticationForm, TOTPVerificationForm


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        """Override form_valid to check for 2FA before completing login"""
        user = form.get_user()
        
        # Check if user has 2FA enabled
        if user_has_device(user):
            # Store user_id in session for 2FA verification
            self.request.session['pre_2fa_user_id'] = user.id
            self.request.session['pre_2fa_backend'] = user.backend
            return redirect('accounts:verify_2fa')
        else:
            # No 2FA, proceed with normal login
            login(self.request, user)
            messages.success(self.request, 'Login successful!')
            return redirect(self.get_success_url())


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out!')
    return redirect('accounts:login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('todo:todo_list')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('todo:todo_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@csrf_exempt
def verify_2fa_view(request):
    """View to verify 2FA token during login"""
    # Check if user is in pre-2FA state
    user_id = request.session.get('pre_2fa_user_id')
    if not user_id:
        messages.error(request, 'Invalid session. Please login again.')
        return redirect('accounts:login')
    
    from django.contrib.auth.models import User

    user = User.objects.get(id=user_id)
    
    if request.method == 'POST':
        form = TOTPVerificationForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']
            
            # Get user's TOTP device and verify token
            device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
            if device and device.verify_token(token):
                # Token is valid, complete login
                backend = request.session.get('pre_2fa_backend')
                user.backend = backend
                login(request, user)
                
                # Clean up session
                del request.session['pre_2fa_user_id']
                del request.session['pre_2fa_backend']
                
                messages.success(request, 'Login successful!')
                return redirect('todo:todo_list')
            else:
                messages.error(request, 'Invalid verification code. Please try again.')
    else:
        form = TOTPVerificationForm()
    
    return render(request, 'accounts/verify_2fa.html', {'form': form})

@login_required
def setup_2fa_view(request):
    """View to setup 2FA for the user"""
    user = request.user
    
    # Check if user already has a confirmed device
    existing_device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
    if existing_device:
        messages.info(request, 'Two-factor authentication is already enabled.')
        return redirect('accounts:manage_2fa')
    
    # Get or create unconfirmed device
    device = TOTPDevice.objects.filter(user=user, confirmed=False).first()
    if not device:
        device = TOTPDevice.objects.create(
            user=user,
            name='default',
            confirmed=False
        )
    
    if request.method == 'POST':
        form = TOTPVerificationForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']
            
            # Verify the token
            if device.verify_token(token):
                device.confirmed = True
                device.save()
                messages.success(request, 'Two-factor authentication has been enabled successfully!')
                return redirect('accounts:manage_2fa')
            else:
                messages.error(request, 'Invalid verification code. Please try again.')
    else:
        form = TOTPVerificationForm()
    
    # Generate QR code
    otpauth_url = device.config_url
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(otpauth_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'form': form,
        'qr_code': qr_code_base64,
        'secret_key': device.key,
        'otpauth_url': otpauth_url,
    }
    
    return render(request, 'accounts/setup_2fa.html', context)


@login_required
def manage_2fa_view(request):
    """View to manage 2FA settings"""
    user = request.user
    device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
    
    context = {
        'has_2fa': device is not None,
    }
    
    return render(request, 'accounts/manage_2fa.html', context)


@login_required
@require_http_methods(["POST"])
def disable_2fa_view(request):
    """View to disable 2FA"""
    user = request.user
    
    # Delete all TOTP devices for the user
    TOTPDevice.objects.filter(user=user).delete()
    
    messages.success(request, 'Two-factor authentication has been disabled.')
    return redirect('accounts:manage_2fa')

