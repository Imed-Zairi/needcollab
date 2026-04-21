from django.urls import path
from . import views

urlpatterns = [
    path('needs/', views.NeedListCreate.as_view()),
    path('needs/<int:pk>/', views.NeedDetail.as_view()),
    path('needs/<int:pk>/join/', views.join_need),
    path('needs/<int:need_id>/offers/', views.OfferListCreate.as_view()),
    path('offers/<int:offer_id>/vote/', views.vote_offer),
]
