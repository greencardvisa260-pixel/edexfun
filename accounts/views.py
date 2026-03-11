from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User, SoundSettings
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer


# ── API Views ──────────────────────────────────────────────

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # New users must wait for admin approval
        return Response({
            'message': 'Registration successful. Please wait for admin approval before logging in.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        # Admins and superusers are always allowed; auto-approve if needed
        if user.is_admin_user() or user.is_superuser:
            if not user.is_approved:
                user.is_approved = True
                user.save(update_fields=['is_approved'])
        elif not user.is_approved:
            return Response(
                {'error': 'Your account is pending admin approval. Please check back later.'},
                status=status.HTTP_403_FORBIDDEN
            )
        from rest_framework.authtoken.models import Token
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})


class LogoutAPIView(APIView):
    def post(self, request):
        try:
            request.user.auth_token.delete()
        except Exception:
            pass
        return Response({'message': 'Logged out.'})


class MeAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class TeacherListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.is_admin_user() or self.request.user.is_superuser:
            return User.objects.filter(role='teacher').order_by('-created_at')
        return User.objects.none()


class TeacherDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.is_admin_user() or self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.none()


class ApproveTeacherAPIView(APIView):
    """Toggle teacher approval status."""
    def post(self, request, pk):
        if not (request.user.is_admin_user() or request.user.is_superuser):
            return Response({'error': 'Admin only'}, status=403)
        try:
            teacher = User.objects.get(pk=pk, role='teacher')
        except User.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        teacher.is_approved = not teacher.is_approved
        teacher.save()
        return Response({'id': teacher.id, 'is_approved': teacher.is_approved})


class SoundSettingsAPIView(APIView):
    """GET returns current settings. POST updates (admin only)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        s = SoundSettings.get()
        return Response({
            'bg_music_enabled': s.bg_music_enabled,
            'correct_sound_enabled': s.correct_sound_enabled,
            'wrong_sound_enabled': s.wrong_sound_enabled,
            'winner_fanfare_enabled': s.winner_fanfare_enabled,
            'tile_click_enabled': s.tile_click_enabled,
            'powerup_sound_enabled': s.powerup_sound_enabled,
            'master_volume': s.master_volume,
        })

    def post(self, request):
        if not (request.user.is_admin_user() or request.user.is_superuser):
            return Response({'error': 'Admin only'}, status=403)
        s = SoundSettings.get()
        fields = ['bg_music_enabled', 'correct_sound_enabled', 'wrong_sound_enabled',
                  'winner_fanfare_enabled', 'tile_click_enabled', 'powerup_sound_enabled',
                  'master_volume']
        for f in fields:
            if f in request.data:
                setattr(s, f, request.data[f])
        s.updated_by = request.user
        s.save()
        return Response({'message': 'Saved'})


class AdminStatsAPIView(APIView):
    """Usage stats for the admin dashboard."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (request.user.is_admin_user() or request.user.is_superuser):
            return Response({'error': 'Admin only'}, status=403)

        from games.models import Game
        from gameplay.models import GameSession
        from django.db.models import Count, Sum, F, ExpressionWrapper, DurationField, Q
        from django.utils import timezone
        from datetime import timedelta

        total_games = Game.objects.count()
        total_public = Game.objects.filter(visibility='public').count()
        total_private = Game.objects.filter(visibility='private').count()
        total_teachers = User.objects.filter(role='teacher').count()
        pending_approvals = User.objects.filter(role='teacher', is_approved=False).count()
        total_sessions = GameSession.objects.count()

        # Most played games with total hours played
        popular_games_qs = (
            Game.objects
            .annotate(play_count=Count('sessions'))
            .filter(play_count__gt=0)
            .order_by('-play_count')[:8]
        )
        popular_games = []
        for g in popular_games_qs:
            finished = GameSession.objects.filter(game=g, status='finished', ended_at__isnull=False)
            total_minutes = 0
            for s in finished:
                diff = (s.ended_at - s.created_at).total_seconds() / 60
                total_minutes += max(0, min(diff, 300))  # cap at 5h per session
            popular_games.append({
                'id': g.id,
                'title': g.title,
                'play_count': g.play_count,
                'owner__username': g.owner.username,
                'total_hours': round(total_minutes / 60, 1),
            })

        # Sessions per user (activity) with per-teacher public/private counts
        teachers_qs = (
            User.objects.filter(role='teacher')
            .annotate(session_count=Count('hosted_sessions'))
            .order_by('-session_count')[:20]
        )
        user_activity = []
        for u in teachers_qs:
            pub = Game.objects.filter(owner=u, visibility='public').count()
            priv = Game.objects.filter(owner=u, visibility='private').count()
            user_activity.append({
                'id': u.id,
                'username': u.username,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'session_count': u.session_count,
                'last_login': u.last_login,
                'is_approved': u.is_approved,
                'public_games': pub,
                'private_games': priv,
                'total_games': pub + priv,
            })

        # Recent sessions (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_sessions = (
            GameSession.objects
            .filter(created_at__gte=week_ago)
            .select_related('game', 'host')
            .order_by('-created_at')[:20]
            .values('id', 'game__title', 'host__username', 'status', 'created_at', 'ended_at')
        )

        return Response({
            'totals': {
                'games': total_games,
                'public_games': total_public,
                'private_games': total_private,
                'teachers': total_teachers,
                'pending_approvals': pending_approvals,
                'sessions': total_sessions,
            },
            'popular_games': popular_games,
            'user_activity': user_activity,
            'recent_sessions': list(recent_sessions),
        })



class SiteSettingsAPIView(APIView):
    """GET returns current site/branding settings. POST updates (admin only)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from accounts.models import SiteSettings
        s = SiteSettings.get()
        return Response({
            'logo_type': s.logo_type,
            'logo_text': s.logo_text,
            'logo_image_url': s.logo_image_url,
        })

    def post(self, request):
        if not (request.user.is_admin_user() or request.user.is_superuser):
            return Response({'error': 'Admin only'}, status=403)
        from accounts.models import SiteSettings
        s = SiteSettings.get()
        s.logo_type = request.data.get('logo_type', s.logo_type)
        s.logo_text = request.data.get('logo_text', s.logo_text)
        s.logo_image_url = request.data.get('logo_image_url', s.logo_image_url)
        s.updated_by = request.user
        s.save()
        return Response({'logo_type': s.logo_type, 'logo_text': s.logo_text, 'logo_image_url': s.logo_image_url})


class TeacherExportGamesCSV(APIView):
    """Export all games of a specific teacher as a single CSV."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if not (request.user.is_admin_user() or request.user.is_superuser):
            return Response({'error': 'Admin only'}, status=403)
        import csv as csv_mod
        import io
        from games.models import Game
        teacher = User.objects.get(pk=pk)
        games = Game.objects.filter(owner=teacher).prefetch_related('questions')
        output = io.StringIO()
        writer = csv_mod.writer(output)
        writer.writerow(['game_title', 'tile_number', 'question_type', 'question',
                         'correct_answer', 'option_a', 'option_b', 'option_c', 'option_d',
                         'points', 'special', 'time_limit', 'hint', 'image_url'])
        for game in games:
            for q in game.questions.all():
                writer.writerow([
                    game.title, q.tile_number, q.question_type, q.question_text,
                    q.correct_answer, q.option_a, q.option_b, q.option_c, q.option_d,
                    q.points, q.special, q.time_limit, q.hint, q.image_url
                ])
        import django.http
        response = django.http.HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{teacher.username}_games.csv"'
        return response


# ── Page Views ─────────────────────────────────────────────

def login_page(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            # Admins and Django superusers are ALWAYS allowed in — no approval needed.
            # Also auto-approve them so the DB stays consistent (handles createsuperuser).
            if user.is_admin_user() or user.is_superuser:
                if not user.is_approved:
                    user.is_approved = True
                    user.save(update_fields=['is_approved'])
                login(request, user)
                return redirect('/dashboard/')
            elif user.is_approved:
                login(request, user)
                return redirect('/dashboard/')
            else:
                error = 'Your account is pending admin approval. Please wait for an administrator to approve your account.'
        else:
            error = 'Invalid username or password.'
    return render(request, 'login.html', {'error': error})


def register_page(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    if request.method == 'POST':
        from .serializers import RegisterSerializer
        data = {
            'username': request.POST.get('username'),
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
            'password2': request.POST.get('password2'),
            'first_name': request.POST.get('first_name', ''),
            'last_name': request.POST.get('last_name', ''),
            'school': request.POST.get('school', ''),
        }
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return render(request, 'register.html', {'success': True})
        return render(request, 'register.html', {'errors': serializer.errors, 'data': data})
    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')
