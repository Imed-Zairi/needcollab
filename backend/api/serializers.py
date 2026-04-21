from rest_framework import serializers
from .models import Need, Offer, Vote


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'user', 'choice']


class OfferSerializer(serializers.ModelSerializer):
    votes = VoteSerializer(many=True, read_only=True)
    accept_count = serializers.SerializerMethodField()
    reject_count = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = ['id', 'need', 'seller_name', 'price', 'description', 'created_at', 'votes', 'accept_count', 'reject_count']

    def get_accept_count(self, obj):
        return obj.votes.filter(choice='accept').count()

    def get_reject_count(self, obj):
        return obj.votes.filter(choice='reject').count()


class NeedSerializer(serializers.ModelSerializer):
    offers = OfferSerializer(many=True, read_only=True)
    collaborators_count = serializers.SerializerMethodField()

    class Meta:
        model = Need
        fields = ['id', 'title', 'description', 'creator', 'collaborators_count', 'created_at', 'offers']

    def get_collaborators_count(self, obj):
        return obj.collaborators.count()
