from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='teacher')
    school = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False, help_text="Admin must approve before teacher can log in")

    def is_admin_user(self):
        return self.role == 'admin'

    def is_teacher(self):
        return self.role == 'teacher'

    def __str__(self):
        return f"{self.username} ({self.role})"


class SoundSettings(models.Model):
    """Global sound settings configurable by admin."""
    bg_music_enabled = models.BooleanField(default=True)
    correct_sound_enabled = models.BooleanField(default=True)
    wrong_sound_enabled = models.BooleanField(default=True)
    winner_fanfare_enabled = models.BooleanField(default=True)
    tile_click_enabled = models.BooleanField(default=True)
    powerup_sound_enabled = models.BooleanField(default=True)
    master_volume = models.FloatField(default=0.7, help_text="0.0 to 1.0")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Sound Settings"

    def save(self, *args, **kwargs):
        # Singleton — always use pk=1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Sound Settings"


class SiteSettings(models.Model):
    """Global branding / site settings configurable by admin."""
    logo_type = models.CharField(
        max_length=10, choices=[('text', 'Text'), ('image', 'Image')], default='text'
    )
    logo_text = models.CharField(max_length=60, default='BamBoozle', blank=True)
    logo_image_url = models.URLField(blank=True, help_text="URL to logo image (WebP preferred)")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Site Settings"

    def save(self, *args, **kwargs):
        self.pk = 1  # singleton
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={'logo_type': 'text', 'logo_text': 'BamBoozle'})
        return obj

    def __str__(self):
        return "Site Settings"
