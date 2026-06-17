from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0004_migrate_candidate_data"),
        ("candidates", "0003_finalize_candidate_schema"),
    ]

    operations = [
        migrations.AlterField(
            model_name="application",
            name="resume_file",
            field=models.FileField(upload_to="applications/%Y/%m/"),
        ),
    ]
