from app.database.base import Base
import app.models.ats_match  # noqa: F401
import app.models.resume  # noqa: F401
import app.models.users  # noqa: F401
import app.models.job  # noqa: F401
import app.models.emails  # noqa: F401
from sqlalchemy import text
from app.database.session import engine

with engine.begin() as conn:
    tables = [t.name for t in Base.metadata.sorted_tables if t.schema is None]
    if not tables:
        print('No tables found.')
        raise SystemExit(0)

    names = ', '.join(tables)
    conn.execute(text(f'TRUNCATE TABLE {names} RESTART IDENTITY CASCADE'))
    print(f'TRUNCATED {len(tables)} tables: {names}')
