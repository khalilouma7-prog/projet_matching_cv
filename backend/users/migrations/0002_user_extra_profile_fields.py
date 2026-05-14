# Colonnes profil sur User : soit déjà en base (ancien schéma), soit ajoutées par ce script.

from django.db import migrations, models


def _sqlite_user_columns(schema_editor):
    with schema_editor.connection.cursor() as c:
        c.execute("PRAGMA table_info(users_user)")
        return {row[1] for row in c.fetchall()}


def forwards_add_columns_if_needed(apps, schema_editor):
    if schema_editor.connection.vendor != "sqlite":
        return
    cols = _sqlite_user_columns(schema_editor)
    with schema_editor.connection.cursor() as c:
        if "cv_file" not in cols:
            c.execute(
                "ALTER TABLE users_user ADD COLUMN cv_file varchar(100) NULL"
            )
        if "localisation" not in cols:
            c.execute(
                "ALTER TABLE users_user ADD COLUMN localisation varchar(100) NOT NULL DEFAULT ''"
            )
        if "experience_annees" not in cols:
            c.execute(
                "ALTER TABLE users_user ADD COLUMN experience_annees integer NOT NULL DEFAULT 0"
            )
        if "competences" not in cols:
            c.execute(
                "ALTER TABLE users_user ADD COLUMN competences text NOT NULL DEFAULT ''"
            )


def backwards_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    state_operations = [
        migrations.AddField(
            model_name="user",
            name="cv_file",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="localisation",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="user",
            name="experience_annees",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="user",
            name="competences",
            field=models.TextField(blank=True, default=""),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations,
            database_operations=[
                migrations.RunPython(forwards_add_columns_if_needed, backwards_noop)
            ],
        ),
    ]
