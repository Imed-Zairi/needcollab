from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Need(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='needs')
    collaborators = models.ManyToManyField(User, related_name='joined_needs', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Offer(models.Model):
    need = models.ForeignKey(Need, on_delete=models.CASCADE, related_name='offers')
    seller_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller_name} - {self.price}"


class Vote(models.Model):
    ACCEPT = 'accept'
    REJECT = 'reject'
    CHOICES = [(ACCEPT, 'Accept'), (REJECT, 'Reject')]

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.CharField(max_length=10, choices=CHOICES)

    class Meta:
        unique_together = ('offer', 'user')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, default='')
    location = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return f'Profile({self.user.username})'


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
