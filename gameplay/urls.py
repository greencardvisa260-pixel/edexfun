from django.urls import path
from . import views

urlpatterns = [
    path('create/<int:game_pk>/', views.CreateSessionView.as_view(), name='create-session'),
    path('<int:pk>/', views.SessionDetailView.as_view(), name='session-detail'),
    path('<int:pk>/start/', views.StartSessionView.as_view(), name='start-session'),
    path('<int:pk>/reveal/', views.RevealTileView.as_view(), name='reveal-tile'),
    path('<int:pk>/award/', views.AwardPointsView.as_view(), name='award-points'),
    path('<int:pk>/end/', views.EndSessionView.as_view(), name='end-session'),
]
