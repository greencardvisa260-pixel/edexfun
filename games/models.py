from django.db import models
from accounts.models import User


class Game(models.Model):
    GRID_SIZE_CHOICES = [(3, '3x3'), (4, '4x4'), (5, '5x5'), (6, '6x6')]
    VISIBILITY_CHOICES = [('public', 'Public'), ('private', 'Private')]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games')
    grid_size = models.IntegerField(choices=GRID_SIZE_CHOICES, default=4)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='private')
    subject = models.CharField(max_length=100, blank=True)
    grade_level = models.CharField(max_length=50, blank=True)
    cover_image_url = models.URLField(blank=True, help_text='WebP image URL for game card thumbnail')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.owner.username}"

    def total_tiles(self):
        return self.grid_size * self.grid_size

    def question_count(self):
        return self.questions.count()


class Question(models.Model):
    TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('text', 'Text Q&A'),
    ]
    SPECIAL_CHOICES = [
        ('none', 'None'),
        ('double_points', 'Double Points'),
        ('steal', 'Steal'),
        ('bomb', 'Bomb'),
        ('swap', 'Swap Scores'),
    ]

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='questions')
    tile_number = models.IntegerField()
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='text')
    question_text = models.TextField()
    correct_answer = models.CharField(max_length=500)
    points = models.IntegerField(default=100)
    special = models.CharField(max_length=20, choices=SPECIAL_CHOICES, default='none')

    # For multiple choice
    option_a = models.CharField(max_length=300, blank=True)
    option_b = models.CharField(max_length=300, blank=True)
    option_c = models.CharField(max_length=300, blank=True)
    option_d = models.CharField(max_length=300, blank=True)

    # Optional image
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    image_url = models.URLField(blank=True)

    time_limit = models.IntegerField(default=30, help_text="Seconds to answer")
    hint = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ['tile_number']
        unique_together = ['game', 'tile_number']

    def __str__(self):
        return f"Tile {self.tile_number}: {self.question_text[:50]}"

    def get_image(self):
        if self.image:
            return self.image.url
        return self.image_url or None
