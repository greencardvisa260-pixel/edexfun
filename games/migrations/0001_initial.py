from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('grid_size', models.IntegerField(choices=[(3, '3x3'), (4, '4x4'), (5, '5x5')], default=4)),
                ('visibility', models.CharField(choices=[('public', 'Public'), ('private', 'Private')], default='private', max_length=10)),
                ('subject', models.CharField(blank=True, max_length=100)),
                ('grade_level', models.CharField(blank=True, max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games', to='accounts.user')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tile_number', models.IntegerField()),
                ('question_type', models.CharField(choices=[('multiple_choice', 'Multiple Choice'), ('true_false', 'True/False'), ('text', 'Text Q&A')], default='text', max_length=20)),
                ('question_text', models.TextField()),
                ('correct_answer', models.CharField(max_length=500)),
                ('points', models.IntegerField(default=100)),
                ('special', models.CharField(choices=[('none', 'None'), ('double_points', 'Double Points'), ('steal', 'Steal'), ('bomb', 'Bomb')], default='none', max_length=20)),
                ('option_a', models.CharField(blank=True, max_length=300)),
                ('option_b', models.CharField(blank=True, max_length=300)),
                ('option_c', models.CharField(blank=True, max_length=300)),
                ('option_d', models.CharField(blank=True, max_length=300)),
                ('image', models.ImageField(blank=True, null=True, upload_to='question_images/')),
                ('image_url', models.URLField(blank=True)),
                ('time_limit', models.IntegerField(default=30)),
                ('hint', models.CharField(blank=True, max_length=300)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='games.game')),
            ],
            options={'ordering': ['tile_number']},
        ),
        migrations.AlterUniqueTogether(
            name='question',
            unique_together={('game', 'tile_number')},
        ),
    ]
