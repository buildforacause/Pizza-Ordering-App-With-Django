from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="IndexPage"),
    path('login/', views.login_here, name="LoginPage"),
    path('logout/', views.logout_here, name="LogoutPage"),
    path('register/', views.register_here, name="RegisterPage"),
    path('about/', views.about, name="AboutPage"),
    path('category/<cat>/', views.catWisePizza, name="CatWisePizza"),
    path('add_cart/<pizza_uuid>/', views.add_cart, name="AddToCart"),
    path('delete_cart/<pizza_uuid>/', views.delete_cart, name="DeleteFromCart"),
    path('cart/', views.cart, name="Cart"),
    path('my_orders/', views.orders, name="MyOrders"),
    path('success/', views.success, name="PaymentSuccess"),
]
