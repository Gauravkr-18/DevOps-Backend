from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import Category, Workshop, Enrollment, UserProfile, Wishlist, Review, PasswordReset
from .serializers import (
    CategorySerializer, WorkshopSerializer, EnrollmentSerializer,
    UserSerializer, UserRegistrationSerializer, UserProfileSerializer,
    WishlistSerializer, ReviewSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class WorkshopViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing workshops
    """
    queryset = Workshop.objects.filter(is_active=True)
    serializer_class = WorkshopSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', None)
        difficulty = self.request.query_params.get('difficulty', None)
        search = self.request.query_params.get('search', None)

        if category:
            queryset = queryset.filter(category__slug=category)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing enrollments
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an enrollment"""
        enrollment = self.get_object()
        enrollment.status = 'cancelled'
        enrollment.save()
        return Response({'status': 'enrollment cancelled'})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """Register a new user"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    """Login user"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Please provide both username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'message': 'Login successful'
        })
    
    return Response(
        {'error': 'Invalid credentials'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    """Logout user"""
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logout successful'})
    except:
        return Response({'error': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """Get current user profile with enrollments"""
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    enrollments = Enrollment.objects.filter(user=user, status='enrolled')
    wishlist = Wishlist.objects.filter(user=user)
    
    return Response({
        'user': UserSerializer(user).data,
        'profile': UserProfileSerializer(profile).data,
        'enrollments': EnrollmentSerializer(enrollments, many=True).data,
        'wishlist': WishlistSerializer(wishlist, many=True).data,
        'total_enrollments': enrollments.count(),
        'wishlist_count': wishlist.count()
    })


class WishlistViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing wishlist
    """
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Toggle wishlist status for a workshop"""
        workshop_id = request.data.get('workshop') or request.data.get('workshop_id')
        if not workshop_id:
            return Response({'error': 'workshop_id required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            workshop = Workshop.objects.get(id=workshop_id)
            wishlist_item = Wishlist.objects.filter(user=request.user, workshop=workshop).first()
            
            if wishlist_item:
                wishlist_item.delete()
                return Response({'action': 'removed', 'wishlisted': False})
            else:
                Wishlist.objects.create(user=request.user, workshop=workshop)
                return Response({'action': 'added', 'wishlisted': True})
        except Workshop.DoesNotExist:
            return Response({'error': 'Workshop not found'}, status=status.HTTP_404_NOT_FOUND)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reviews
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        workshop_id = self.request.query_params.get('workshop', None)
        if workshop_id:
            return Review.objects.filter(workshop_id=workshop_id)
        return Review.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def request_password_reset(request):
    """Request password reset - verify username and email match"""
    username = request.data.get('username')
    email = request.data.get('email')
    
    if not username or not email:
        return Response(
            {'error': 'Both username and email are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Check if user exists with matching username and email
        user = User.objects.get(username=username, email=email)
        
        # Invalidate any existing unused tokens for this user
        from .models import PasswordReset
        PasswordReset.objects.filter(user=user, used=False).update(used=True)
        
        # Create new reset token
        reset_token = PasswordReset.objects.create(user=user)
        
        return Response({
            'message': 'Username and email verified! You can now reset your password.',
            'token': str(reset_token.token),
            'expires_in': '24 hours'
        })
    except User.DoesNotExist:
        return Response(
            {'error': 'Username and email do not match. Please try again.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def reset_password(request):
    """Reset password using token"""
    from .models import PasswordReset
    from django.utils import timezone
    
    token = request.data.get('token')
    new_password = request.data.get('new_password')
    
    if not token or not new_password:
        return Response(
            {'error': 'Token and new password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(new_password) < 6:
        return Response(
            {'error': 'Password must be at least 6 characters long'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        reset_token = PasswordReset.objects.get(token=token)
        
        if not reset_token.is_valid():
            if reset_token.used:
                return Response(
                    {'error': 'This reset link has already been used'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {'error': 'This reset link has expired'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Reset the password
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        
        # Mark token as used
        reset_token.used = True
        reset_token.save()
        
        return Response({
            'message': 'Password reset successful! You can now login with your new password.',
            'username': user.username
        })
    except PasswordReset.DoesNotExist:
        return Response(
            {'error': 'Invalid reset token'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def hello_world(request):
    """Simple hello world endpoint"""
    return Response({
        'message': 'Welcome to Workshop Enrollment API!',
        'status': 'success'
    })
