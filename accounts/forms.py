from django import forms
from .models import UserRole
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

CLASS_INPUT = 'w-full px-4 py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-800 focus:border-transparent transition duration-200'

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = UserRole
        fields = ['phone', 'profile_picture']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
    
    def save(self, commit=True):
        user_role = super().save(commit=False)
        if commit:
            user_role.user.first_name = self.cleaned_data['first_name']
            user_role.user.last_name = self.cleaned_data['last_name']
            user_role.user.save()
            user_role.save()
        return user_role
    
class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password'] 
    
    username = forms.CharField(widget=forms.TextInput(attrs={
        "id":"username",
        "placeholder":"Enter username...",
        "class":CLASS_INPUT
    }))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "id":"password",
        "placeholder":"password...",
        "class":CLASS_INPUT
    }))

class UserForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': CLASS_INPUT, 
            'placeholder': 'Enter your email address',
            'id': 'email'
        })
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': CLASS_INPUT, 
            'placeholder': 'Create a password',
            'id': 'password1'
        })
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': CLASS_INPUT, 
            'placeholder': 'Confirm your password',
            'id': 'password2'
        })
    )
    
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

class UserRoleForm(forms.ModelForm):
    class Meta:
        model = UserRole
        fields = ['user_type']
        widgets = {
            'user_type': forms.RadioSelect()
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter to only show landlord and renter options
        self.fields['user_type'].choices = [
            ('landlord', 'Landlord/አከራይ'),
            ('renter', 'Renter/ተከራይ')
        ]