# backend/urls.py

from . import views
from django.urls import path
from .views import CreateOrderView, OrderListView, CartItemDeleteView
from .models import Order, OrderItem  


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', ChangePasswordView.as_view()),
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('reset-password/<uidb64>/<token>/', ResetPasswordConfirmView.as_view()),
    path('dashboard/', dashboard_view),
    path('brands/', BrandListCreateView.as_view()),       # now supports POST
    path('products/', ProductListCreateView.as_view()),   # now supports POST
    path('cart/', CartItemListCreateView.as_view()),
    path('order/create/', CreateOrderView.as_view()),
    path('orders/', OrderListView.as_view()),
    path('cart/<int:pk>/delete/', CartItemDeleteView.as_view()),  # 🗑️ Delete Cart Item
    path('orders/', OrderListView.as_view()),  # 🧾 All user order
 
]
