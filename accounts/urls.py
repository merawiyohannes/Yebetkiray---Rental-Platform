from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from .forms import LoginForm



urlpatterns = [
    path('signup/', views.signup_view, name='signup_view'),
    path('login/', LoginView.as_view(template_name='accounts/login.html', authentication_form=LoginForm), name='login_view'),
    path('logout/', LogoutView.as_view(), name='logout_view'),
    path('edit/', views.edit_profile, name="edit_view"),
    path("<int:id>/favorite/", views.toggle_favorite_view, name='favorite')
    
]
