from django.urls import path
from . import views

urlpatterns = [
    path('', views.GameListCreateView.as_view(), name='game-list'),
    path('<int:pk>/', views.GameDetailView.as_view(), name='game-detail'),
    path('<int:pk>/questions/', views.QuestionCreateView.as_view(), name='question-create'),
    path('questions/<int:pk>/', views.QuestionDetailView.as_view(), name='question-detail'),
    path('<int:pk>/upload-csv/', views.CSVUploadView.as_view(), name='csv-upload'),
    path('csv-template/', views.CSVTemplateView.as_view(), name='csv-template'),
]
