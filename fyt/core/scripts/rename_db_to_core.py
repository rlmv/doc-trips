from django.db import connection

def run():
    '''
    manage.py runscript rename_db_to_core
    '''
    old_name = 'db'
    new_name = 'core'
    models = ['tripsyear']

    with connection.cursor() as cursor:
        # Rename model
        cursor.execute("UPDATE django_content_type SET app_label='{}' WHERE app_label='{}'".format(new_name, old_name))
        cursor.execute("UPDATE django_migrations SET app='{}' WHERE app='{}'".format(new_name, old_name))

        for model in models:
            cursor.execute("ALTER TABLE {old_name}_{model_name} RENAME TO {new_name}_{model_name}".format(
                old_name=old_name, new_name=new_name, model_name=model))
