from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db.models import Sum

# Create your models here.


class BaseModel(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class PizzaCategory(BaseModel):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name


class Pizza(BaseModel):
    category = models.ForeignKey(PizzaCategory, on_delete=models.CASCADE, related_name="pizzas")
    name = models.CharField(max_length=100)
    price = models.FloatField()
    desc = models.CharField(max_length=500)
    image = models.ImageField(upload_to='pizza')

    def __str__(self):
        return self.name


class Cart(BaseModel):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='carts')
    is_paid = models.BooleanField(default=False)
    instamojo_id = models.CharField(max_length=1000, default="")

    def get_total(self):
        total = CartItems.objects.filter(cart=self).aggregate(Sum('pizza__price'))['pizza__price__sum']
        if total:
            return total
        return 0

    def __str__(self):
        return self.user.username


class CartItems(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)

    def __str__(self):
        return self.pizza.name
