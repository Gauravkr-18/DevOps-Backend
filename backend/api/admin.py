from django.contrib import admin
from .models import Category, Workshop, Enrollment, UserProfile, Wishlist, Review, PasswordReset


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'duration', 'instructor', 'is_active', 'enrolled_count', 'average_rating']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ['category', 'difficulty', 'is_active']
    search_fields = ['title', 'instructor']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'workshop', 'status', 'enrolled_at']
    list_filter = ['status', 'enrolled_at']
    search_fields = ['user__username', 'workshop__title']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'created_at']
    search_fields = ['user__username', 'user__email']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'workshop', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'workshop__title']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'workshop', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'workshop__title', 'comment']
