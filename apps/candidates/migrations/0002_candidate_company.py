import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("companies", "0001_initial"),
        ("candidates", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="candidate",
            name="company",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="candidates",
                to="companies.company",
            ),
        ),
    ]
