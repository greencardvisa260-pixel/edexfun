import csv
import io
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Game, Question
from .serializers import GameSerializer, GameListSerializer, QuestionSerializer


class GameListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GameListSerializer
        return GameSerializer

    def get_queryset(self):
        user = self.request.user
        visibility = self.request.query_params.get('visibility', 'all')
        if user.is_admin_user():
            qs = Game.objects.all()
        else:
            # Teachers see their own + public games
            from django.db.models import Q
            qs = Game.objects.filter(Q(owner=user) | Q(visibility='public'))

        if visibility == 'mine':
            qs = qs.filter(owner=user)
        elif visibility == 'public':
            qs = qs.filter(visibility='public')

        search = self.request.query_params.get('search', '')
        if search:
            qs = qs.filter(title__icontains=search)

        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GameSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user():
            return Game.objects.all()
        from django.db.models import Q
        return Game.objects.filter(Q(owner=user) | Q(visibility='public'))

    def update(self, request, *args, **kwargs):
        game = self.get_object()
        if game.owner != request.user and not request.user.is_admin_user():
            return Response({'error': 'Permission denied'}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        game = self.get_object()
        if game.owner != request.user and not request.user.is_admin_user():
            return Response({'error': 'Permission denied'}, status=403)
        return super().destroy(request, *args, **kwargs)


class CSVUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk=None):
        game = get_object_or_404(Game, pk=pk)
        if game.owner != request.user and not request.user.is_admin_user():
            return Response({'error': 'Permission denied'}, status=403)

        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response({'error': 'No file provided'}, status=400)

        if not csv_file.name.endswith('.csv'):
            return Response({'error': 'File must be a CSV'}, status=400)

        try:
            decoded = csv_file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded))
            created = []
            errors = []
            max_tiles = game.total_tiles()

            for i, row in enumerate(reader, 1):
                try:
                    tile_num = int(row.get('tile_number', i))
                    if tile_num > max_tiles:
                        errors.append(f"Row {i}: tile_number {tile_num} exceeds grid size ({max_tiles} tiles)")
                        continue

                    # Delete existing question for this tile if present
                    Question.objects.filter(game=game, tile_number=tile_num).delete()

                    q_type = row.get('question_type', 'text').strip().lower()
                    if q_type not in ['multiple_choice', 'true_false', 'text']:
                        q_type = 'text'

                    special = row.get('special', 'none').strip().lower()
                    if special not in ['none', 'double_points', 'steal', 'bomb', 'swap']:
                        special = 'none'

                    Question.objects.create(
                        game=game,
                        tile_number=tile_num,
                        question_type=q_type,
                        question_text=row.get('question', '').strip(),
                        correct_answer=row.get('correct_answer', '').strip(),
                        points=int(row.get('points', 100)),
                        special=special,
                        option_a=row.get('option_a', '').strip(),
                        option_b=row.get('option_b', '').strip(),
                        option_c=row.get('option_c', '').strip(),
                        option_d=row.get('option_d', '').strip(),
                        image_url=row.get('image_url', '').strip(),
                        time_limit=int(row.get('time_limit', 30)),
                        hint=row.get('hint', '').strip(),
                    )
                    created.append(tile_num)
                except Exception as e:
                    errors.append(f"Row {i}: {str(e)}")

            return Response({
                'created': len(created),
                'tiles': created,
                'errors': errors,
                'message': f"Successfully imported {len(created)} questions."
            })

        except Exception as e:
            return Response({'error': f'CSV parse error: {str(e)}'}, status=400)


class CSVTemplateView(APIView):
    def get(self, request):
        import django.http
        response = django.http.HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bamboozle_template.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'tile_number', 'question_type', 'question',
            'correct_answer', 'option_a', 'option_b', 'option_c', 'option_d',
            'points', 'special', 'time_limit', 'hint', 'image_url'
        ])
        writer.writerow([1, 'multiple_choice', 'What is the capital of France?',
                         'Paris', 'London', 'Paris', 'Berlin', 'Madrid',
                         100, 'none', 30, 'Think about the Eiffel Tower', ''])
        writer.writerow([2, 'true_false', 'The Earth is flat.',
                         'False', 'True', 'False', '', '',
                         100, 'none', 20, '', ''])
        writer.writerow([3, 'text', 'Name the largest planet in our solar system.',
                         'Jupiter', '', '', '', '',
                         200, 'double_points', 30, 'It has a big red spot', ''])
        writer.writerow([4, 'multiple_choice', 'Which element has symbol Au?',
                         'Gold', 'Silver', 'Gold', 'Platinum', 'Bronze',
                         150, 'steal', 25, 'Think periodic table', ''])
        return response


class QuestionCreateView(generics.CreateAPIView):
    serializer_class = QuestionSerializer

    def perform_create(self, serializer):
        game = get_object_or_404(Game, pk=self.kwargs['pk'])
        if game.owner != self.request.user and not self.request.user.is_admin_user():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied()
        serializer.save(game=game)


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
