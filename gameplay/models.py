import json
from django.db import models
from accounts.models import User
from games.models import Game


class GameSession(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('active', 'Active'),
        ('finished', 'Finished'),
    ]

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='sessions')
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_sessions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    current_tile = models.IntegerField(null=True, blank=True)
    teams_data = models.TextField(default='[]')
    revealed_tiles = models.TextField(default='[]')
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    @property
    def teams(self):
        return json.loads(self.teams_data)

    @teams.setter
    def teams(self, value):
        self.teams_data = json.dumps(value)

    @property
    def revealed(self):
        return json.loads(self.revealed_tiles)

    @revealed.setter
    def revealed(self, value):
        self.revealed_tiles = json.dumps(value)

    def __str__(self):
        return f"Session: {self.game.title} ({self.status})"

    def initialize_teams(self, team_names):
        teams = [
            {'id': i + 1, 'name': name, 'score': 0, 'color': colors[i]}
            for i, name in enumerate(team_names)
        ]
        self.teams = teams
        self.save()
        return teams

    def award_points(self, team_id, points, action='add'):
        teams = self.teams
        for team in teams:
            if team['id'] == team_id:
                if action == 'add':
                    team['score'] += points
                elif action == 'subtract':
                    team['score'] = max(0, team['score'] - points)
                elif action == 'set':
                    team['score'] = points
        self.teams = teams
        self.save()
        return teams

    def reveal_tile(self, tile_number):
        revealed = self.revealed
        if tile_number not in revealed:
            revealed.append(tile_number)
            self.revealed = revealed
            self.save()
        return revealed


colors = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#A8E6CF']
