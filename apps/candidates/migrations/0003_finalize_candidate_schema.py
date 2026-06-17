import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("candidates", "0002_candidate_company"),
        ("applications", "0004_migrate_candidate_data"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="candidate",
            name="parsed_resume_text",
        ),
        migrations.RemoveField(
            model_name="candidate",
            name="resume_file",
        ),
        migrations.AlterField(
            model_name="candidate",
            name="company",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="candidates",
                to="companies.company",
            ),
        ),
        migrations.AddConstraint(
            model_name="candidate",
            constraint=models.UniqueConstraint(
                fields=("company", "email"),
                name="uniq_candidate_per_company_email",
            ),
        ),
    ]
