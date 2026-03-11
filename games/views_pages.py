from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import path
from .models import Game


def index(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    return redirect('/accounts/login/')


@login_required
def dashboard(request):
    from django.db.models import Q, Count
    user = request.user
    if user.is_admin_user():
        my_games = Game.objects.all()
    else:
        my_games = Game.objects.filter(owner=user)
    public_games = Game.objects.filter(visibility='public').exclude(owner=user)

    ctx = {
        'my_games': my_games[:1000],
        'public_games': public_games[:1000],
        'user': user,
    }

    # Admin-only stats injected directly into dashboard context
    if user.is_admin_user() or user.is_superuser:
        from accounts.models import User as UserModel
        from gameplay.models import GameSession
        ctx['admin_stats'] = {
            'total_games': Game.objects.count(),
            'total_teachers': UserModel.objects.filter(role='teacher').count(),
            'pending_approvals': UserModel.objects.filter(role='teacher', is_approved=False).count(),
            'total_sessions': GameSession.objects.count(),
        }
        # Pending teachers for quick action
        ctx['pending_teachers'] = UserModel.objects.filter(
            role='teacher', is_approved=False
        ).order_by('-created_at')[:5]
        # Most played games
        ctx['popular_games'] = (
            Game.objects
            .annotate(play_count=Count('sessions'))
            .order_by('-play_count')[:4]
        )

    return render(request, 'dashboard.html', ctx)


@login_required
def game_editor(request, pk=None):
    game = None
    if pk:
        game = get_object_or_404(Game, pk=pk)
        if game.owner != request.user and not request.user.is_admin_user():
            return redirect('/dashboard/')
    return render(request, 'editor.html', {'game': game})


@login_required
def game_play(request, pk):
    game = get_object_or_404(Game, pk=pk)
    return render(request, 'play.html', {'game': game})


@login_required
def manage_teachers(request):
    if not (request.user.is_admin_user() or request.user.is_superuser):
        return redirect('/dashboard/')
    from accounts.models import User
    teachers = User.objects.filter(role='teacher')
    return render(request, 'teachers.html', {'teachers': teachers})


@login_required
def admin_panel(request):
    if not (request.user.is_admin_user() or request.user.is_superuser):
        return redirect('/dashboard/')
    return render(request, 'admin_panel.html')


@login_required
def manage_teachers(request):
    if not (request.user.is_admin_user() or request.user.is_superuser):
        return redirect('/dashboard/')
    return redirect('/admin-panel/')


urlpatterns = [
    path('', index, name='index'),
    path('dashboard/', dashboard, name='dashboard'),
    path('game/new/', game_editor, name='game-new'),
    path('game/<int:pk>/edit/', game_editor, name='game-edit'),
    path('game/<int:pk>/play/', game_play, name='game-play'),
    path('teachers/', manage_teachers, name='teachers'),
    path('admin-panel/', admin_panel, name='admin-panel'),
]
