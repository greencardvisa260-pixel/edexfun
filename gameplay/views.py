from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import GameSession
from games.models import Game, Question


class CreateSessionView(APIView):
    def post(self, request, game_pk):
        game = get_object_or_404(Game, pk=game_pk)
        session = GameSession.objects.create(game=game, host=request.user, status='waiting')
        team_names = request.data.get('teams', ['Team 1', 'Team 2'])
        teams = session.initialize_teams(team_names)
        return Response({
            'session_id': session.id,
            'game': {'id': game.id, 'title': game.title, 'grid_size': game.grid_size},
            'teams': teams,
            'status': session.status,
        }, status=201)


class SessionDetailView(APIView):
    def get(self, request, pk):
        session = get_object_or_404(GameSession, pk=pk)
        from games.serializers import GameSerializer
        return Response({
            'session_id': session.id,
            'game': {
                'id': session.game.id,
                'title': session.game.title,
                'grid_size': session.game.grid_size,
                'questions': [
                    {
                        'tile_number': q.tile_number,
                        'question_type': q.question_type,
                        'question_text': q.question_text,
                        'correct_answer': q.correct_answer,
                        'points': q.points,
                        'special': q.special,
                        'option_a': q.option_a,
                        'option_b': q.option_b,
                        'option_c': q.option_c,
                        'option_d': q.option_d,
                        'time_limit': q.time_limit,
                        'hint': q.hint,
                        'image_src': q.get_image(),
                    }
                    for q in session.game.questions.all()
                ]
            },
            'teams': session.teams,
            'revealed_tiles': session.revealed,
            'current_tile': session.current_tile,
            'status': session.status,
        })


class RevealTileView(APIView):
    def post(self, request, pk):
        session = get_object_or_404(GameSession, pk=pk)
        tile_number = request.data.get('tile_number')
        if not tile_number:
            return Response({'error': 'tile_number required'}, status=400)

        revealed = session.reveal_tile(int(tile_number))
        session.current_tile = tile_number
        session.save()

        # Fetch question for this tile
        question = None
        try:
            q = session.game.questions.get(tile_number=tile_number)
            question = {
                'tile_number': q.tile_number,
                'question_type': q.question_type,
                'question_text': q.question_text,
                'correct_answer': q.correct_answer,
                'points': q.points,
                'special': q.special,
                'option_a': q.option_a,
                'option_b': q.option_b,
                'option_c': q.option_c,
                'option_d': q.option_d,
                'time_limit': q.time_limit,
                'hint': q.hint,
                'image_src': q.get_image(),
            }
        except Exception:
            pass

        return Response({
            'revealed_tiles': revealed,
            'current_tile': tile_number,
            'question': question,
        })


class AwardPointsView(APIView):
    def post(self, request, pk):
        session = get_object_or_404(GameSession, pk=pk)
        team_id = request.data.get('team_id')
        points = request.data.get('points', 0)
        action = request.data.get('action', 'add')  # add, subtract

        if not team_id:
            return Response({'error': 'team_id required'}, status=400)

        teams = session.award_points(int(team_id), int(points), action)
        return Response({'teams': teams})


class EndSessionView(APIView):
    def post(self, request, pk):
        session = get_object_or_404(GameSession, pk=pk)
        session.status = 'finished'
        session.ended_at = timezone.now()
        session.save()

        # Sort teams by score
        teams = sorted(session.teams, key=lambda t: t['score'], reverse=True)
        return Response({
            'status': 'finished',
            'final_scores': teams,
            'winner': teams[0] if teams else None,
        })


class StartSessionView(APIView):
    def post(self, request, pk):
        session = get_object_or_404(GameSession, pk=pk)
        session.status = 'active'
        session.save()
        return Response({'status': 'active', 'session_id': session.id})
