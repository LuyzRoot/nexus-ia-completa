from nexus.repositories.base import BaseRepository
from nexus.models.user import User
from database.session import AsyncSessionLocal
from sqlalchemy.future import select

class UserRepository(BaseRepository):
    """User repository"""
    
    async def create(self, email: str, username: str, hashed_password: str, **kwargs):
        async with AsyncSessionLocal() as db:
            user = User(email=email, username=username, hashed_password=hashed_password)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
    
    async def get_by_id(self, id: str):
        async with AsyncSessionLocal() as db:
            stmt = select(User).where(User.id == id)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str):
        async with AsyncSessionLocal() as db:
            stmt = select(User).where(User.email == email)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
    
    async def get_all(self):
        async with AsyncSessionLocal() as db:
            stmt = select(User)
            result = await db.execute(stmt)
            return result.scalars().all()
    
    async def update(self, id: str, **kwargs):
        async with AsyncSessionLocal() as db:
            stmt = select(User).where(User.id == id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                for key, value in kwargs.items():
                    setattr(user, key, value)
                await db.commit()
                await db.refresh(user)
            return user
    
    async def delete(self, id: str):
        async with AsyncSessionLocal() as db:
            stmt = select(User).where(User.id == id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                await db.delete(user)
                await db.commit()
            return user
