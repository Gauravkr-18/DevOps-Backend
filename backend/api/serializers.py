from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Workshop, Enrollment, UserProfile, Wishlist, Review


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'phone', 'avatar', 'created_at']
        read_only_fields = ['id', 'created_at']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    workshop_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'description', 'workshop_count']
        read_only_fields = ['id']

    def get_workshop_count(self, obj):
        return obj.workshops.filter(is_active=True).count()


class WorkshopSerializer(serializers.ModelSerializer):
    """Serializer for Workshop model"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    enrolled_count = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    is_enrolled = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()
    user_review = serializers.SerializerMethodField()

    class Meta:
        model = Workshop
        fields = [
            'id', 'title', 'slug', 'description', 'category', 'category_name',
            'difficulty', 'duration', 'instructor', 'max_students', 
            'image_url', 'is_active', 'enrolled_count', 'is_full', 
            'average_rating', 'review_count', 'is_enrolled', 'is_wishlisted',
            'user_review', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'enrolled_count', 'is_full', 'average_rating', 'review_count']

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(
                user=request.user, 
                workshop=obj, 
                status='enrolled'
            ).exists()
        return False

    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Wishlist.objects.filter(
                user=request.user, 
                workshop=obj
            ).exists()
        return False

    def get_user_review(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                review = Review.objects.get(user=request.user, workshop=obj)
                return {'rating': review.rating, 'comment': review.comment}
            except Review.DoesNotExist:
                return None
        return None


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment model"""
    workshop = WorkshopSerializer(read_only=True)
    workshop_id = serializers.IntegerField(write_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'user', 'user_name', 'workshop', 'workshop_id', 
            'status', 'enrolled_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'enrolled_at', 'updated_at']

    def validate_workshop_id(self, value):
        try:
            workshop = Workshop.objects.get(id=value)
            if workshop.is_full:
                raise serializers.ValidationError("This workshop is full")
            if not workshop.is_active:
                raise serializers.ValidationError("This workshop is not active")
        except Workshop.DoesNotExist:
            raise serializers.ValidationError("Workshop not found")
        return value

    def create(self, validated_data):
        workshop_id = validated_data.pop('workshop_id')
        workshop = Workshop.objects.get(id=workshop_id)
        validated_data['workshop'] = workshop
        return super().create(validated_data)


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for Wishlist model"""
    workshop = WorkshopSerializer(read_only=True)
    workshop_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'workshop', 'workshop_id', 'added_at']
        read_only_fields = ['id', 'user', 'added_at']

    def create(self, validated_data):
        workshop_id = validated_data.pop('workshop_id')
        workshop = Workshop.objects.get(id=workshop_id)
        validated_data['workshop'] = workshop
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    workshop_title = serializers.CharField(source='workshop.title', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'user_name', 'workshop', 'workshop_title', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
