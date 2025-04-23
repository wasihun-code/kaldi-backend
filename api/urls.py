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

router.register(r'address', AddressViewSet, basename='address')
router.register(r'transaction', TransactionViewSet, basename='transaction')
router.register(r'order', OrderViewSet, basename='order')
router.register(r'wallet', WalletViewSet, basename='wallet')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'discount', DiscountViewSet, basename='discount')
router.register(r'item', ItemViewSet, basename='item')
router.register(r'notification', NotificationViewSet, basename='notification')
router.register(r'user', UserViewSet, basename='user')
router.register(r'bid', BidViewSet, basename='bid')
router.register(r'rating', RatingViewSet, basename='rating')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'order-items', OrderItemViewSet, basename='order-item')
router.register(r'used-items', UsedItemViewSet, basename='used-item')

urlpatterns = [
    # api views
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    
    # Telegram Login
    path('telegram-login/', TelegramLoginView.as_view(), name='telegram-login'),
    path('telegram-register/', TelegramRegisterView.as_view(), name='telegram-register'),   

    path('user/detail/', get_user_details, name='single_user'),
    path('vendor/customer/', VendorCustomerViewSet.as_view({'get': 'list'}), name='vendor_customer'),
    path('register/', RegistrationView.as_view(), name='register'),
    
    path('', include(router.urls)),  # Remove the leading slash here
    
    # simple_jwt auth views
]