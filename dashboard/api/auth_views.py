from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from ..models.profile_models import Profile
from ..serializers.profile_serializers import ProfileSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    phone_number = request.data.get('phone_number')
    address = request.data.get('address')
    city = request.data.get('city')
    state = request.data.get('state')
    country = request.data.get('country')
    zip_code = request.data.get('zip_code')
    date_of_birth = request.data.get('date_of_birth')
    bio = request.data.get('bio')
    
    # Check for required fields
    if not username or not password or not email or not date_of_birth:
        return Response({'error': 'Please provide all required fields'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check for duplicate username
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check for duplicate email
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate email format
    try:
        validate_email(email)
    except ValidationError:
        return Response({'error': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create the user
    user = User.objects.create_user(username=username, password=password, email=email)
    
    # Check if the profile already exists
    profile, created = Profile.objects.get_or_create(user=user)
    profile.phone_number = phone_number
    profile.address = address
    profile.city = city
    profile.state = state
    profile.country = country
    profile.zip_code = zip_code
    profile.date_of_birth = date_of_birth
    profile.bio = bio
    profile.save()
    
    return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)