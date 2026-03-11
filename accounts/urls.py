from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # API
    path('api/register/', views.RegisterAPIView.as_view(), name='api-register'),
    path('api/login/', views.LoginAPIView.as_view(), name='api-login'),
    path('api/logout/', views.LogoutAPIView.as_view(), name='api-logout'),
    path('api/me/', views.MeAPIView.as_view(), name='api-me'),
    path('api/teachers/', views.TeacherListAPIView.as_view(), name='api-teachers'),
    path('api/teachers/<int:pk>/', views.TeacherDetailAPIView.as_view(), name='api-teacher-detail'),
    path('api/teachers/<int:pk>/approve/', views.ApproveTeacherAPIView.as_view(), name='api-teacher-approve'),
    path('api/sound-settings/', views.SoundSettingsAPIView.as_view(), name='api-sound-settings'),
    path('api/admin-stats/', views.AdminStatsAPIView.as_view(), name='api-admin-stats'),
    path('api/site-settings/', views.SiteSettingsAPIView.as_view(), name='api-site-settings'),
    path('api/teachers/<int:pk>/export-csv/', views.TeacherExportGamesCSV.as_view(), name='api-teacher-export-csv'),
]
