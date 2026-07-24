import os
from pathlib import Path
from sqlalchemy import text
from app.database.database import engine

print('DATABASE_URL', os.getenv('DATABASE_URL', ''))
print('ENGINE_URL', str(engine.url))
print('DB_EXISTS', Path('crime_intelligence.db').exists())
print('DB_SIZE', Path('crime_intelligence.db').stat().st_size if Path('crime_intelligence.db').exists() else 'N/A')

with engine.begin() as conn:
    tables = [
        ('case_master', 'CaseMaster'),
        ('accused', 'Accused'),
        ('victim', 'Victim'),
        ('arrest_surrender', 'ArrestSurrender'),
        ('crime_head', 'CrimeHead'),
        ('crime_sub_head', 'CrimeSubHead'),
        ('employee', 'Employee'),
        ('district', 'District'),
        ('unit', 'Unit'),
        ('act', 'Act'),
        ('section', 'Section'),
        ('court', 'Court'),
    ]
    for tbl, model_name in tables:
        try:
            count = conn.execute(text(f'SELECT COUNT(*) FROM {tbl}')).scalar_one()
            print(f'{tbl}:{count}')
        except Exception as e:
            print(f'{tbl}:ERROR:{e}')

    try:
        rows = conn.execute(text("SELECT MIN(registered_date), MAX(registered_date), MIN(incident_date), MAX(incident_date) FROM case_master")).fetchall()
        print('CASE_DATES', rows[0])
    except Exception as e:
        print('CASE_DATES:ERROR', e)
