from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from instamojo_wrapper import Instamojo
from django.conf import settings

# Create your views here.

api = Instamojo(api_key=settings.API_KEY,
                auth_token=settings.AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/')


def home(request):
    pizzas = Pizza.objects.all()
    return render(request, "home.html", {'pizzas': pizzas})


def login_here(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in Successfully!')
            return redirect("/")
        else:
            messages.error(request, 'Invalid credentials!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request, "login.html")


@login_required(login_url='/login/')
def logout_here(request):
    logout(request)
    messages.success(request, 'Logged out Successfully!')
    return redirect("/")


def register_here(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        if not username.isalnum():
            messages.error(request, 'Your username must only contain letters and numbers!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if User.objects.filter(username=username, email=email).exists():
            messages.warning(request, "You already have an account! Login instead!")
            return redirect("/login")
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        try:
            new_user = User.objects.create_user(username=username, email=email, password=password)
            new_user.save()
            messages.success(request, 'Your account has been created successfully! Login Now!')
            return redirect("/login")
        except:
            messages.error(request, 'Your username must be unique! Please choose an unique username.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request, "register.html")


def catWisePizza(request, cat):
    cat_wise_pizzas = []
    pizzas = Pizza.objects.all()
    for cats in pizzas:
        if str(cats.category) == str(cat):
            cat_wise_pizzas.append(cats)
    return render(request, "catwisepizza.html", {'pizzas': cat_wise_pizzas})


@login_required(login_url='/login/')
def add_cart(request, pizza_uuid):
    if request.user.is_authenticated:
        user = request.user
        pizza_obj = Pizza.objects.get(uid=pizza_uuid)
        cart, _ = Cart.objects.get_or_create(user=user, is_paid=False)
        cart_items = CartItems.objects.create(
            cart=cart,
            pizza=pizza_obj
        )
        messages.success(request, f"Successfully added {pizza_obj.name} to your cart!")
        return redirect("/")
    else:
        messages.error(request, "You need to login first!!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='/login/')
def delete_cart(request, pizza_uuid):
    user = request.user
    pizza_obj = Pizza.objects.get(uid=pizza_uuid)
    cart_obj = Cart.objects.get(user=user, is_paid=False)
    cart_items = CartItems.objects.filter(cart=cart_obj, pizza=pizza_obj)[0].delete()
    messages.success(request, f"Removed {pizza_obj.name} successfully from your cart!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='/login/')
def cart(request):
    cart_obj = Cart.objects.get_or_create(user=request.user, is_paid=False)[0]
    response = api.payment_request_create(
        amount=cart_obj.get_total(),
        purpose='PizzaXpress Order',
        buyer_name=request.user.username,
        send_email=True,
        email="GGinthechat100@gmail.com",
        redirect_url="http://127.0.0.1:8000/success/"
    )
    try:
        cart_obj.instamojo_id = response['payment_request']['id']
        cart_obj.save()
    except KeyError:
        return render(request, "cart.html", {'cart': cart_obj})
    return render(request, "cart.html", {'cart': cart_obj, 'payment_url': response['payment_request']['longurl']})


@login_required(login_url='/login/')
def orders(request):
    all_orders = Cart.objects.filter(is_paid=True, user=request.user)
    return render(request, "orders.html", {'orders': all_orders})


@login_required(login_url='/login/')
def success(request):
    payment_request = request.GET.get('payment_request_id', '')
    cart = Cart.objects.get(instamojo_id=payment_request)
    cart.is_paid = True
    cart.save()
    messages.success(request, "Order has been placed successfully! Hope you enjoy it!")
    return redirect("/my_orders/")


def about(request):
    return render(request, "about.html")

