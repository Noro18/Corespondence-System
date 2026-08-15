from django.db import migrations


def forward(apps, schema_editor):
    OutboundLetter = apps.get_model("outbound_letters", "OutboundLetter")
    OutboundLetter.objects.filter(category="ASU").update(category="PED")


def reverse(apps, schema_editor):
    OutboundLetter = apps.get_model("outbound_letters", "OutboundLetter")
    OutboundLetter.objects.filter(category="PED").update(category="ASU")


class Migration(migrations.Migration):

    dependencies = [
        ("outbound_letters", "0005_alter_outboundletter_category"),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]