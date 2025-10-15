from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
from datetime import timedelta


class Category(models.Model):
    """Workshop categories like Frontend, Backend, AI/ML, etc."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']


class Workshop(models.Model):
    """Workshop/Course model"""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='workshops')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    duration = models.CharField(max_length=50)  # e.g., "3 Days Intensive"
    instructor = models.CharField(max_length=100)
    max_students = models.IntegerField(default=30)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def enrolled_count(self):
        return self.enrollments.filter(status='enrolled').count()

    @property
    def is_full(self):
        return self.enrolled_count >= self.max_students

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    @property
    def review_count(self):
        return self.reviews.count()

    class Meta:
        ordering = ['-created_at']


class Enrollment(models.Model):
    """User enrollment in workshops"""
    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.workshop.title}"

    class Meta:
        unique_together = ['user', 'workshop']
        ordering = ['-enrolled_at']


class UserProfile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Wishlist(models.Model):
    """User's wishlist/favorites"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.workshop.title}"

    class Meta:
        unique_together = ['user', 'workshop']
        ordering = ['-added_at']


class Review(models.Model):
    """Workshop reviews and ratings"""
    RATING_CHOICES = [(i, i) for i in range(1, 6)]  # 1-5 stars

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.workshop.title} - {self.rating} stars"


class PasswordReset(models.Model):
    """Password reset token model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_resets')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_valid(self):
        """Check if token is still valid"""
        return not self.used and timezone.now() < self.expires_at

    def __str__(self):
        return f"Password reset for {self.user.username} - {'Valid' if self.is_valid() else 'Invalid'}"

    class Meta:
        ordering = ['-created_at']
