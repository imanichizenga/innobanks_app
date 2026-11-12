from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AboutFAQ",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, blank=True, null=True)),
                (
                    "question",
                    models.CharField(
                        blank=True,
                        help_text="Question shown in the about us FAQ section.",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "answer",
                    models.TextField(blank=True, help_text="Answer for the about us FAQ question.", null=True),
                ),
                (
                    "order",
                    models.PositiveIntegerField(
                        blank=True,
                        default=0,
                        help_text="Display order of FAQ items.",
                        null=True,
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        blank=True,
                        default=True,
                        help_text="Controls whether this FAQ is visible.",
                        null=True,
                    ),
                ),
                (
                    "menu_item",
                    models.ForeignKey(
                        blank=True,
                        help_text="About us menu item this FAQ belongs to.",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="faqs",
                        to="website.aboutmenuitem",
                    ),
                ),
            ],
            options={"ordering": ["order", "question"]},
        ),
    ]
