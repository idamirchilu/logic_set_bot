import logging
from app.config import config

logger = logging.getLogger(__name__)

class ScoringSystem:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def calculate_points(self, exercise_difficulty: int, is_correct: bool, question_type: str = None) -> int:
        """Calculate points based on exercise difficulty and correctness"""
        base_points = config.points_correct_answer if is_correct else 0
        difficulty_bonus = exercise_difficulty * 2
        return base_points + difficulty_bonus
    
    async def update_user_score(self, user_id: int, points: int, question_type: str = None):
        """Update user's score in the database"""
        return await self.db_manager.update_user_score(user_id, points, question_type)
    
    def get_user_level(self, score: int) -> int:
        """Determine user level based on score"""
        level = 1
        level_thresholds = [100, 300, 600, 1000, 1500]
        for i, threshold in enumerate(level_thresholds):
            if score >= threshold:
                level = i + 2
        return level
    
    def get_level_progress(self, score: int, level: int) -> float:
        """Calculate progress to next level"""
        level_thresholds = [100, 300, 600, 1000, 1500]
        
        if level - 2 < 0:
            current_threshold = 0
        else:
            current_threshold = level_thresholds[level - 2] if level - 2 < len(level_thresholds) else level_thresholds[-1]
        
        next_threshold = level_thresholds[level - 1] if level - 1 < len(level_thresholds) else level_thresholds[-1] * 2
        
        progress = (score - current_threshold) / (next_threshold - current_threshold) * 100
        return min(100, max(0, progress))
    
    async def get_leaderboard(self, top_n: int = 10):
        """Get top users by score"""
        # This would need to be implemented based on your database structure
        # For now, return an empty list
        return []