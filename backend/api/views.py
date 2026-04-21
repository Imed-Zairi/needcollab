from rest_framework import generics, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Need, Offer, Vote, Profile
from .serializers import (
    NeedSerializer, NeedMiniSerializer, OfferSerializer,
    VoteSerializer, ProfileSerializer, ProfileUpdateSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    if User.objects.filter(username=username).exists():
        return Response({'error': "Nom d'utilisateur déjà pris."}, status=400)
    user = User.objects.create_user(username=username, password=password, email=email)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'user_id': user.id, 'username': user.username})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Identifiants invalides.'}, status=400)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'user_id': user.id, 'username': user.username})


# ── PROFILE ───────────────────────────────────────────

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def my_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return Response(ProfileSerializer(profile).data)


@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(ProfileSerializer(profile).data)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def my_needs(request):
    needs = Need.objects.filter(creator=request.user).order_by('-created_at')
    return Response(NeedMiniSerializer(needs, many=True).data)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def my_collabs(request):
    needs = request.user.joined_needs.all().order_by('-created_at')
    return Response(NeedMiniSerializer(needs, many=True).data)


# ── NEEDS ─────────────────────────────────────────────

class NeedListCreate(generics.ListCreateAPIView):
    queryset = Need.objects.all().order_by('-created_at')
    serializer_class = NeedSerializer

    def get_permissions(self):
        return [IsAuthenticated()] if self.request.method == 'POST' else [AllowAny()]

    def get_authenticators(self):
        return [TokenAuthentication()] if self.request.method == 'POST' else []

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class NeedDetail(generics.RetrieveAPIView):
    queryset = Need.objects.all()
    serializer_class = NeedSerializer
    permission_classes = [AllowAny]


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def join_need(request, pk):
    need = Need.objects.get(pk=pk)
    need.collaborators.add(request.user)
    return Response({'status': 'joined'})


# ── OFFERS ────────────────────────────────────────────

class OfferListCreate(generics.ListCreateAPIView):
    serializer_class = OfferSerializer

    def get_permissions(self):
        return [IsAuthenticated()] if self.request.method == 'POST' else [AllowAny()]

    def get_authenticators(self):
        return [TokenAuthentication()] if self.request.method == 'POST' else []

    def get_queryset(self):
        return Offer.objects.filter(need_id=self.kwargs['need_id'])

    def perform_create(self, serializer):
        serializer.save(need_id=self.kwargs['need_id'])


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def vote_offer(request, offer_id):
    offer = Offer.objects.get(pk=offer_id)
    choice = request.data.get('choice')
    vote, _ = Vote.objects.update_or_create(offer=offer, user=request.user, defaults={'choice': choice})
    return Response(VoteSerializer(vote).data, status=status.HTTP_200_OK)
