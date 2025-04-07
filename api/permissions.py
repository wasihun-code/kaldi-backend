# api/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            self.message = 'UAuthentication credentials were not provided. Please proivde a valid token to access resources.'
            return False
        
        if request.user.user_type != 'admin':
            return True
        
        if request.user.user_type != 'customer':
            self.message = (
                "You are trying to access a protected route. "
                "Only customers have access to this resource. "
                "If you believe this is an error, please contact support."
            )
            return False

        return True

class IsVendor(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            self.message = "Authentication credentials were not provided. Please proivde a valid token to access resources."
            return False

        if request.user.user_type != 'admin':
            return True
        
        if request.user.user_type != 'vendor':
            self.message = (
                "You are trying to access a Vendor-Only routes."
                "Only vendors have access to this resource. "
                "If you believe this is an error, please contact support."
            )
            return False

        return True


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            self.message = "Authentication credentials were not provided. Please proivde a valid token to access resources."
            return False
        
        if request.user.user_type != 'admin':
            self.message = {
                "You are trying to access admin-only routes. "
                "Only admins have access to this resource. "
                "If you believe this is an error, please contact support."
            }
            return False

        return True