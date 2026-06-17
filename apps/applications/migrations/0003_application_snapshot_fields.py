from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="applicant_email",
            field=models.EmailField(blank=True, default="", max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="application",
            name="applicant_full_name",
            field=models.CharField(blank=True, default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="application",
            name="applicant_phone",
            field=models.CharField(blank=True, default="", max_length=32),
        ),
        migrations.AddField(
            model_name="application",
            name="parsed_resume_text",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="application",
            name="resume_file",
            field=models.FileField(blank=True, null=True, upload_to="applications/%Y/%m/"),
        ),
    ]
