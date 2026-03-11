from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_is_approved_soundsettings'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo_type', models.CharField(choices=[('text', 'Text'), ('image', 'Image')], default='text', max_length=10)),
                ('logo_text', models.CharField(blank=True, default='BamBoozle', max_length=60)),
                ('logo_image_url', models.URLField(blank=True, help_text='URL to logo image (WebP preferred)')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Site Settings',
            },
        ),
    ]
