# Generated by Django 2.1.5 on 2019-01-17 22:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("api", "0038_step_path")]

    operations = [
        migrations.AlterModelOptions(name="step", options={"ordering": ("step_num",)}),
        migrations.RemoveField(model_name="step", name="task_name"),
    ]
