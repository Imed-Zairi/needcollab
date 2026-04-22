from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('register', views.register),
    path('login', views.login_view),
    path('logout', views.logout_view),
    path('profile', views.profile),
    path('profile/edit', views.edit_profile),
    path('needs/create', views.create_need),
    path('needs/<int:need_id>', views.need_detail),
    path('needs/<int:need_id>/edit', views.edit_need),
    path('needs/<int:need_id>/delete', views.delete_need),
    path('needs/<int:need_id>/archive', views.archive_need),
    path('needs/<int:need_id>/join', views.join_need),
    path('needs/<int:need_id>/offers/create', views.create_offer),
    path('offers/<int:offer_id>/vote', views.vote),
]
