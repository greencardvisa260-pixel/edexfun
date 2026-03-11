from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_game_6x6'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='cover_image_url',
            field=models.URLField(blank=True, help_text='WebP image URL for game card thumbnail'),
        ),
    ]
