from app.database.base import Base
from app.database.session import engine
from app.models.ats_match import ATSMatch
from app.models.resume import Resume
from app.models.users import User
from app.models.job import Job
from app.models.emails import Email



def create_tables():

    Base.metadata.create_all(bind=engine)