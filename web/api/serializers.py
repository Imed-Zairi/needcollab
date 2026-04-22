from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Need, Offer, Vote, Profile


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'user', 'choice']


class OfferSerializer(serializers.ModelSerializer):
    votes = VoteSerializer(many=True, read_only=True)
    accept_count = serializers.SerializerMethodField()
    reject_count = serializers.SerializerMethodField()
    need = serializers.PrimaryKeyRelatedField(read_only=True)

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
    creator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Need
        fields = ['id', 'title', 'description', 'creator', 'collaborators_count', 'created_at', 'offers']

    def get_collaborators_count(self, obj):
        return obj.collaborators.count()


class NeedMiniSerializer(serializers.ModelSerializer):
    offers_count = serializers.SerializerMethodField()
    collaborators_count = serializers.SerializerMethodField()

    class Meta:
        model = Need
        fields = ['id', 'title', 'description', 'created_at', 'offers_count', 'collaborators_count']

    def get_offers_count(self, obj):
        return obj.offers.count()

    def get_collaborators_count(self, obj):
        return obj.collaborators.count()


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    needs_count = serializers.SerializerMethodField()
    collabs_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['username', 'email', 'bio', 'location', 'date_joined', 'needs_count', 'collabs_count']

    def get_needs_count(self, obj):
        return obj.user.needs.count()

    def get_collabs_count(self, obj):
        return obj.user.joined_needs.count()


class ProfileUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', required=False)
    username = serializers.CharField(source='user.username', required=False)

    class Meta:
        model = Profile
        fields = ['username', 'email', 'bio', 'location']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if 'email' in user_data:
            instance.user.email = user_data['email']
        if 'username' in user_data:
            instance.user.username = user_data['username']
        instance.user.save()
        instance.bio = validated_data.get('bio', instance.bio)
        instance.location = validated_data.get('location', instance.location)
        instance.save()
        return instance
