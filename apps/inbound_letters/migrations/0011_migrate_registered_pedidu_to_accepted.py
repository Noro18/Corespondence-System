from django.db import migrations


def forward(apps, schema_editor):
    InboundLetter = apps.get_model("inbound_letters", "InboundLetter")
    InboundLetter.objects.filter(
        category="PED", status="REG"
    ).update(status="APR")


def reverse(apps, schema_editor):
    InboundLetter = apps.get_model("inbound_letters", "InboundLetter")
    InboundLetter.objects.filter(
        category="PED", status="APR"
    ).update(status="REG")


class Migration(migrations.Migration):

    dependencies = [
        ("inbound_letters", "0010_migrate_letter_categories"),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]