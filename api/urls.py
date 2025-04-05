from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
    TokenRefreshView, 
    TokenBlacklistView,
)

from api.views import (
    AddressViewSet, TransactionViewSet, OrderViewSet, WalletViewSet,
    InventoryViewSet, DiscountViewSet, ItemViewSet,
    CartViewSet, BidViewSet, UserViewSet, get_user_details
)


router = DefaultRouter()

router.register(prefix=r'address', viewset=AddressViewSet, basename='address')
router.register(prefix=r'transaction', viewset=TransactionViewSet, basename='transaction')
router.register(prefix=r'order', viewset=OrderViewSet, basename='order')
router.register(prefix=r'wallet', viewset=WalletViewSet, basename='wallet')

router.register(prefix=r'inventory', viewset=InventoryViewSet, basename='inventory')
router.register(prefix=r'discount', viewset=DiscountViewSet, basename='discount')
router.register(prefix=r'item', viewset=ItemViewSet, basename='item')

router.register(prefix=r'user', viewset=UserViewSet, basename='user')
router.register(prefix=r'bid', viewset=BidViewSet, basename='bid')
router.register(prefix=r'cart', viewset=CartViewSet, basename='cart')



urlpatterns = [
    # simple_jwt auth views
    path('/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    # blacklist token
    path('/token/blacklist', TokenBlacklistView.as_view(), name='token_blacklist'),
    # api views
    path('/', include(router.urls), name='api'),
    path('/user/detail', get_user_details, name='single_user')
    # auth views
]