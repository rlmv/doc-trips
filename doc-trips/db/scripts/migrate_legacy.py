
from db.legacy.migrate import migrate

"""
manage.py runscript migrate_legacy
"""

def run():
    migrate()
