from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='grid_size',
            field=models.IntegerField(
                choices=[(3, '3x3'), (4, '4x4'), (5, '5x5'), (6, '6x6')],
                default=4
            ),
        ),
    ]
