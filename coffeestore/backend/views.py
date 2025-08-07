from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .models import Brand, Product  # if you created these
from .serializers import BrandSerializer, ProductSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import OrderSerializer
from django.conf import settings


# -----------------------
# 🔹 1. Register View
# -----------------------
class RegisterView(APIView):
    def post(self, request):
        data = request.data
        if data['password'] != data['confirm_password']:
            return Response({"error": "Passwords do not match"}, status=400)
        if User.objects.filter(username=data['username']).exists():
            return Response({"error": "Username already exists"}, status=400)
        user = User.objects.create_user(
            username=data['username'],
            email=data.get('email', ''),
            password=data['password']
        )
        return Response({"message": "User registered"}, status=201)

# -----------------------
# 🔹 2. Change Password
# -----------------------
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data['old_password']
        new_password = request.data['new_password']
        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect"}, status=400)
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully"})

# -----------------------
# 🔹 3. Forgot Password
# -----------------------
class ForgotPasswordView(APIView):
    def post(self, request):
        print("✅ ForgotPasswordView called")  # Add this
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"http://localhost:8000/api/reset-password/{uid}/{token}/"
            print(f"Password reset link: {reset_link}")  
            # You can send email here too
            return Response({"message": "Password reset link sent (printed on console)"})
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=400)

# -----------------------
# 🔹 4. Reset Password Confirm
# -----------------------
class ResetPasswordConfirmView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid link"}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=400)

        password = request.data.get('new_password')
        confirm = request.data.get('confirm_password')

        if password != confirm:
            return Response({"error": "Passwords do not match"}, status=400)

        user.set_password(password)
        user.save()
        return Response({"message": "Password reset successful"})

# -----------------------
# 🔹 5. Protected Dashboard View (Optional)
# -----------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    return Response({"message": f"Welcome, {request.user.username}!"})

# -----------------------
# 🔹 6. Brand List (Protected or Public)
# -----------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def brand_list(request):
    brands = Brand.objects.all()
    serializer = BrandSerializer(brands, many=True)
    return Response(serializer.data)

# 🔹 7. Product List (Protected or Public)
# -----------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_list(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


from rest_framework import generics
from rest_framework.permissions import IsAdminUser

class BrandListCreateView(generics.ListCreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

from rest_framework import generics
from .models import CartItem
from .serializers import CartItemSerializer

class CartItemListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

from rest_framework import generics
from .models import CartItem
from .serializers import CartItemSerializer
from rest_framework.permissions import IsAuthenticated

class CartItemDeleteView(generics.DestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)
class CreateOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        print("Creating order...")  
        order = serializer.save(user=self.request.user)
from .models import Order
class CreateOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')