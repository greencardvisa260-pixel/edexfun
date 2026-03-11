from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('waiting', 'Waiting'), ('active', 'Active'), ('finished', 'Finished')], default='waiting', max_length=20)),
                ('current_tile', models.IntegerField(blank=True, null=True)),
                ('teams_data', models.TextField(default='[]')),
                ('revealed_tiles', models.TextField(default='[]')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='games.game')),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hosted_sessions', to='accounts.user')),
            ],
        ),
    ]
