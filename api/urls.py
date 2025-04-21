from django.urls import path, include
from rest_framework.routers import DefaultRouter


from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
    TokenRefreshView, 
    TokenBlacklistView,
)


from api.views import (
    AddressViewSet, TransactionViewSet, OrderViewSet, WalletViewSet,
    InventoryViewSet, DiscountViewSet, ItemViewSet, UsedItemViewSet,
    CartViewSet, BidViewSet, UserViewSet, get_user_details,
    VendorCustomerViewSet, OrderItemViewSet, NotificationViewSet, RatingViewSet,
    TelegramLoginView, RegistrationView, TelegramRegisterView
)

router = DefaultRouter()


router.register(prefix=r'address', viewset=AddressViewSet, basename='address')
router.register(prefix=r'transaction', viewset=TransactionViewSet, basename='transaction')
router.register(prefix=r'order', viewset=OrderViewSet, basename='order')
router.register(prefix=r'wallet', viewset=WalletViewSet, basename='wallet')

router.register(prefix=r'inventory', viewset=InventoryViewSet, basename='inventory')
router.register(prefix=r'discount', viewset=DiscountViewSet, basename='discount')
router.register(prefix=r'item', viewset=ItemViewSet, basename='item')
router.register(prefix='notification', viewset=NotificationViewSet, basename='notification')

router.register(prefix=r'user', viewset=UserViewSet, basename='user')
router.register(prefix=r'bid', viewset=BidViewSet, basename='bid')
router.register(prefix=r'rating', viewset=RatingViewSet, basename='rating')
router.register(prefix=r'cart', viewset=CartViewSet, basename='cart')
router.register(prefix=r'order-items', viewset=OrderItemViewSet, basename='order-item')
router.register(prefix=r'used-items', viewset=UsedItemViewSet, basename='used-item')


urlpatterns = [
    # simple_jwt auth views
    path('/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('/token/blacklist', TokenBlacklistView.as_view(), name='token_blacklist'),
    
    # Telegram Login
    path('/telegram-login/', TelegramLoginView.as_view(), name='telegram-login'),
    path('telegram-register/', TelegramRegisterView.as_view(), name='telegram-register'),   

    # api views
    path('/', include(router.urls), name='api'),
    path('/user/detail', get_user_details, name='single_user'),

    path('/vendor/customer', VendorCustomerViewSet.as_view({
        'get' : 'list'
    }), name='vendor_customer'),
    
    path('/register/', RegistrationView.as_view(), name='register'),
]