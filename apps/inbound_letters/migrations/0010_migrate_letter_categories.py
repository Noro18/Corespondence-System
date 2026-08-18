from django.db import migrations


def forward(apps, schema_editor):
    InboundLetter = apps.get_model("inbound_letters", "InboundLetter")
    InboundLetter.objects.filter(category="ASU").update(category="PED")


def reverse(apps, schema_editor):
    InboundLetter = apps.get_model("inbound_letters", "InboundLetter")
    InboundLetter.objects.filter(category="PED").update(category="ASU")


class Migration(migrations.Migration):

    dependencies = [
        ("inbound_letters", "0009_inboundletter_status_and_indecision"),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]