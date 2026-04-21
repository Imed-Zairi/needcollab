from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Need, Offer, Vote
from .serializers import NeedSerializer, OfferSerializer, VoteSerializer


class NeedListCreate(generics.ListCreateAPIView):
    queryset = Need.objects.all().order_by('-created_at')
    serializer_class = NeedSerializer


class NeedDetail(generics.RetrieveAPIView):
    queryset = Need.objects.all()
    serializer_class = NeedSerializer


@api_view(['POST'])
def join_need(request, pk):
    need = Need.objects.get(pk=pk)
    user_id = request.data.get('user_id')
    user = User.objects.get(pk=user_id)
    need.collaborators.add(user)
    return Response({'status': 'joined'})


class OfferListCreate(generics.ListCreateAPIView):
    serializer_class = OfferSerializer

    def get_queryset(self):
        return Offer.objects.filter(need_id=self.kwargs['need_id'])

    def perform_create(self, serializer):
        serializer.save(need_id=self.kwargs['need_id'])


@api_view(['POST'])
def vote_offer(request, offer_id):
    offer = Offer.objects.get(pk=offer_id)
    user_id = request.data.get('user_id')
    choice = request.data.get('choice')
    user = User.objects.get(pk=user_id)
    vote, _ = Vote.objects.update_or_create(offer=offer, user=user, defaults={'choice': choice})
    return Response(VoteSerializer(vote).data, status=status.HTTP_200_OK)
