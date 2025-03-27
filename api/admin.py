from django.contrib import admin
from .models import (
    User, Address, Wallet, Cart, Discount, Inventory, Item, Order, Transaction,
)
admin.site.register(User)
admin.site.register(Address)
admin.site.register(Wallet)
admin.site.register(Cart)
admin.site.register(Discount)
admin.site.register(Inventory)
admin.site.register(Item)
admin.site.register(Order)
admin.site.register(Transaction)