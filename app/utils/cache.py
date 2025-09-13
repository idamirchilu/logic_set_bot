import hashlib
import logging
from app.config import config
import cachetools

logger = logging.getLogger(__name__)

# Create a TTL cache
ttl_cache = cachetools.TTLCache(maxsize=config.cache_maxsize, ttl=config.cache_ttl)


def hash_query(text: str) -> str:
    """Create a hash of a query for caching"""
    return hashlib.md5(text.encode()).hexdigest()


async def get_cached_response(db_manager, query_hash: str):
    """Get a cached response from database"""
    try:
        # First check in-memory cache
        if query_hash in ttl_cache:
            return ttl_cache[query_hash]

        # Then check database cache
        response = await db_manager.get_cached_response(query_hash)
        if response:
            # Store in memory cache for faster access
            ttl_cache[query_hash] = response
            return response

        return None
    except Exception as e:
        logger.error(f"Error getting cached response: {e}")
        return None


async def cache_response(db_manager, query_hash: str, response: str):
    """Cache a response in both database and memory"""
    try:
        # Store in database cache
        await db_manager.cache_response(query_hash, response)
        # Store in memory cache
        ttl_cache[query_hash] = response
    except Exception as e:
        logger.error(f"Error caching response: {e}")