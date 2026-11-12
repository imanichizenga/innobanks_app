from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0001_add_aboutfaq"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomeEnquirySubmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, blank=True, null=True)),
                ("full_name", models.CharField(blank=True, max_length=255, null=True)),
                ("phone_number", models.CharField(blank=True, max_length=50, null=True)),
                ("email", models.EmailField(blank=True, max_length=254, null=True)),
                ("location", models.CharField(blank=True, max_length=255, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("is_contacted", models.BooleanField(blank=True, default=False, null=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="HomeNotice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, blank=True, null=True)),
                ("title", models.CharField(blank=True, max_length=255, null=True)),
                ("subtitle", models.CharField(blank=True, max_length=255, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("button_text", models.CharField(blank=True, max_length=120, null=True)),
                ("badge_label", models.CharField(blank=True, max_length=100, null=True)),
                ("background_image", models.ImageField(blank=True, null=True, upload_to="homepage/notice/")),
                ("is_active", models.BooleanField(blank=True, default=True, null=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="HomeVideo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, blank=True, null=True)),
                ("title", models.CharField(blank=True, help_text="Video title shown on homepage.", max_length=255, null=True)),
                ("description", models.TextField(blank=True, help_text="Short description for this video slide.", null=True)),
                ("video", models.FileField(blank=True, help_text="Upload homepage video file.", null=True, upload_to="homepage/videos/")),
                (
                    "thumbnail",
                    models.ImageField(
                        blank=True,
                        help_text="Optional thumbnail before visitor plays video.",
                        null=True,
                        upload_to="homepage/videos/thumbnails/",
                    ),
                ),
                ("order", models.PositiveIntegerField(blank=True, default=0, help_text="Controls display ordering.", null=True)),
                ("is_active", models.BooleanField(blank=True, default=True, help_text="Show or hide this video.", null=True)),
                (
                    "home_page",
                    models.ForeignKey(
                        blank=True,
                        help_text="Optional relation to the active home page record.",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="videos",
                        to="website.homepage",
                    ),
                ),
            ],
            options={"ordering": ["order", "-created_at"]},
        ),
    ]
