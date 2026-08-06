from sqlalchemy.orm import Session

from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate


class UserRepository:

    @staticmethod
    def create(db: Session, user: UserCreate):

        db_user = User(**user.model_dump())

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def get(db: Session, user_id: int):

        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    @staticmethod
    def get_by_email(db: Session, email: str):

        return (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

    @staticmethod
    def get_all(db: Session):

        return db.query(User).all()

    @staticmethod
    def update(db: Session, user_id: int, user: UserUpdate):

        db_user = UserRepository.get(db, user_id)

        if not db_user:
            return None

        for key, value in user.model_dump(exclude_unset=True).items():
            setattr(db_user, key, value)

        db.commit()
        db.refresh(db_user)

        return db_user