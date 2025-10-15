from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, WorkshopViewSet, EnrollmentViewSet, WishlistViewSet, ReviewViewSet,
    register, login, logout, user_profile, request_password_reset, reset_password, hello_world
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'workshops', WorkshopViewSet)
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('hello/', hello_world, name='hello'),
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('auth/logout/', logout, name='logout'),
    path('auth/profile/', user_profile, name='user_profile'),
    path('auth/request-password-reset/', request_password_reset, name='request_password_reset'),
    path('auth/reset-password/', reset_password, name='reset_password'),
]
