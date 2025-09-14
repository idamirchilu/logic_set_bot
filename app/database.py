import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
from contextlib import asynccontextmanager

from app.config import config

logger = logging.getLogger(__name__)

# Create declarative base
Base = declarative_base()

class DatabaseManager:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or config.database_url
        
        # Ensure we're using async drivers
        if self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        elif self.database_url.startswith("sqlite://"):
            self.database_url = self.database_url.replace("sqlite://", "sqlite+aiosqlite://")
        
        logger.info(f"Using database URL: {self.database_url}")
        
        # Create async engine with SQLite-optimized settings
        engine_kwargs = {
            "echo": config.debug,
            "future": True
        }
        
        # SQLite-specific optimizations
        if "sqlite" in self.database_url:
            engine_kwargs.update({
                "pool_size": 1,  # SQLite doesn't benefit from connection pooling
                "max_overflow": 0,  # No overflow for SQLite
                "connect_args": {
                    "check_same_thread": False,  # Allow async operations
                    "timeout": 30  # Connection timeout
                }
            })
        else:
            # PostgreSQL settings (if needed)
            engine_kwargs.update({
                "pool_size": 20,
                "max_overflow": 10
            })
        
        self.engine = create_async_engine(self.database_url, **engine_kwargs)
        
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False, future=True
        )
    
    @asynccontextmanager
    async def get_session(self):
        """Get an async database session"""
        session = self.async_session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def init_db(self):
        """Initialize database tables"""
        # Import models here to avoid circular imports
        from app.models.user import User
        from app.models.progress import UserProgress, CachedResponse
        from app.models.question import Question
        
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def recreate_database(self):
        """Drop and recreate all tables"""
        from app.models.user import User
        from app.models.progress import UserProgress, CachedResponse
        from app.models.question import Question
        
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database recreated successfully")
        except Exception as e:
            logger.error(f"Database recreation failed: {e}")
            raise
    
    async def clear_database(self):
        """Clear all data from tables"""
        from app.models.user import User
        from app.models.progress import UserProgress, CachedResponse
        from app.models.question import Question
        
        try:
            async with self.get_session() as session:
                await session.execute(CachedResponse.__table__.delete())
                await session.execute(Question.__table__.delete())
                await session.execute(UserProgress.__table__.delete())
                await session.execute(User.__table__.delete())
                await session.commit()
            logger.info("Database cleared successfully")
        except Exception as e:
            logger.error(f"Database clearing failed: {e}")
            raise
    
    async def add_user(self, user_id: int, username: str, first_name: str, last_name: str):
        """Add a new user to the database"""
        from app.models.user import User
        from app.models.progress import UserProgress
        
        async with self.get_session() as session:
            try:
                # Check if user exists
                existing_user = await session.execute(
                    User.__table__.select().where(User.user_id == user_id)
                )
                if existing_user.scalar():
                    return True  # User already exists
                
                # Create new user
                user = User(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                session.add(user)
                
                # Create user progress
                progress = UserProgress(user_id=user_id)
                session.add(progress)
                
                await session.commit()
                return True
                
            except Exception as e:
                logger.error(f"Error adding user {user_id}: {e}")
                await session.rollback()
                return False
    
    async def update_user_interaction(self, user_id: int):
        """Update user's last interaction timestamp"""
        from app.models.user import User
        
        async with self.get_session() as session:
            try:
                await session.execute(
                    User.__table__.update()
                    .where(User.user_id == user_id)
                    .values(last_interaction=func.now())
                )
                await session.commit()
            except Exception as e:
                logger.error(f"Error updating user interaction for {user_id}: {e}")
                await session.rollback()
    
    async def update_user_score(self, user_id: int, points: int, question_type: str = None):
        """Update user's score and progress"""
        from app.models.progress import UserProgress
        
        async with self.get_session() as session:
            try:
                # Get user progress
                result = await session.execute(
                    UserProgress.__table__.select().where(UserProgress.user_id == user_id)
                )
                progress = result.scalar()
                
                if progress:
                    progress.score += points
                    progress.total_exercises += 1
                    
                    if question_type == "logic":
                        progress.logic_correct += 1
                    elif question_type == "set_theory":
                        progress.set_theory_correct += 1
                    
                    # Update level based on score
                    level_thresholds = [100, 300, 600, 1000, 1500]
                    progress.level = 1
                    for i, threshold in enumerate(level_thresholds):
                        if progress.score >= threshold:
                            progress.level = i + 2
                    
                    await session.commit()
                    return progress.score, progress.level
                
                return 0, 1
                
            except Exception as e:
                logger.error(f"Error updating score for user {user_id}: {e}")
                await session.rollback()
                return 0, 1
    
    async def get_user_progress(self, user_id: int):
        """Get user's progress information"""
        from app.models.progress import UserProgress
        
        async with self.get_session() as session:
            try:
                result = await session.execute(
                    UserProgress.__table__.select().where(UserProgress.user_id == user_id)
                )
                progress = result.scalar()
                
                if progress:
                    return {
                        "score": progress.score,
                        "level": progress.level,
                        "logic_correct": progress.logic_correct,
                        "set_theory_correct": progress.set_theory_correct,
                        "total_exercises": progress.total_exercises
                    }
                return None
                
            except Exception as e:
                logger.error(f"Error getting progress for user {user_id}: {e}")
                return None
    
    async def log_question(self, user_id: int, question_text: str, question_type: str):
        """Log user's question"""
        from app.models.question import Question
        
        async with self.get_session() as session:
            try:
                question = Question(
                    user_id=user_id,
                    question_text=question_text,
                    question_type=question_type
                )
                session.add(question)
                await session.commit()
                return question.id
                
            except Exception as e:
                logger.error(f"Error logging question for user {user_id}: {e}")
                await session.rollback()
                return None
    
    async def cache_response(self, query_hash: str, response_text: str):
        """Cache a response for faster retrieval"""
        from app.models.progress import CachedResponse
        
        async with self.get_session() as session:
            try:
                # Check if already exists
                existing = await session.execute(
                    CachedResponse.__table__.select().where(CachedResponse.query_hash == query_hash)
                )
                if existing.scalar():
                    # Update existing
                    await session.execute(
                        CachedResponse.__table__.update()
                        .where(CachedResponse.query_hash == query_hash)
                        .values(response_text=response_text, created_at=func.now())
                    )
                else:
                    # Create new
                    cached = CachedResponse(
                        query_hash=query_hash,
                        response_text=response_text
                    )
                    session.add(cached)
                
                await session.commit()
                
            except Exception as e:
                logger.error(f"Error caching response: {e}")
                await session.rollback()
    
    async def get_cached_response(self, query_hash: str):
        """Get a cached response if available"""
        from app.models.progress import CachedResponse
        
        async with self.get_session() as session:
            try:
                result = await session.execute(
                    CachedResponse.__table__.select().where(CachedResponse.query_hash == query_hash)
                )
                cached = result.scalar()
                return cached.response_text if cached else None
                
            except Exception as e:
                logger.error(f"Error getting cached response: {e}")
                return None

# Global database instance
db_manager = DatabaseManager()