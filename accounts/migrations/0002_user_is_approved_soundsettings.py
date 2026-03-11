from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_approved',
            field=models.BooleanField(default=False, help_text='Admin must approve before teacher can log in'),
        ),
        migrations.CreateModel(
            name='SoundSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bg_music_enabled', models.BooleanField(default=True)),
                ('correct_sound_enabled', models.BooleanField(default=True)),
                ('wrong_sound_enabled', models.BooleanField(default=True)),
                ('winner_fanfare_enabled', models.BooleanField(default=True)),
                ('tile_click_enabled', models.BooleanField(default=True)),
                ('powerup_sound_enabled', models.BooleanField(default=True)),
                ('master_volume', models.FloatField(default=0.7)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.user')),
            ],
            options={'verbose_name': 'Sound Settings'},
        ),
    ]
