# Generated by Django 2.1.2 on 2018-10-15 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("api", "0004_merge_20181015_1617")]

    operations = [
        migrations.RemoveField(model_name="step", name="flow_name"),
        migrations.AddField(
            model_name="plan",
            name="flow_name",
            field=models.CharField(default="set this", max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="step",
            name="task_name",
            field=models.CharField(default="set this", max_length=64),
            preserve_default=False,
        ),
    ]
