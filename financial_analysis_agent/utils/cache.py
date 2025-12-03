import json
import functools
from typing import Callable, Any, TypeVar, ParamSpec, Coroutine, Optional, List
import inspect
from redis.asyncio import Redis # Use redis.asyncio for async operations
from pydantic import BaseModel # Import BaseModel

P = ParamSpec('P')
R = TypeVar('R')

class CacheManager:
    def __init__(self, redis_client: Redis, default_ttl: int = 300):
        self.redis = redis_client
        self.default_ttl = default_ttl

    def cache(self, key_prefix: str, ttl: Optional[int] = None) -> Callable[[Callable[P, Coroutine[Any, Any, R]]], Callable[P, Coroutine[Any, Any, R]]]:
        """
        A decorator to cache asynchronous function results in Redis.

        Args:
            key_prefix: A string prefix for the Redis key.
            ttl: Time-to-live for the cache entry in seconds. Defaults to self.default_ttl.
        """
        if ttl is None:
            ttl = self.default_ttl

        def decorator(func: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, Coroutine[Any, Any, R]]:
            @functools.wraps(func)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                # Generate cache key based on function name, prefix, and arguments
                # We need to bind the arguments to their names for a consistent key
                bound_args = inspect.signature(func).bind(*args, **kwargs)
                bound_args.apply_defaults()
                cache_key_parts = [key_prefix, func.__name__]
                for name, value in bound_args.arguments.items():
                    # Exclude 'self' or 'cls' from key generation for instance methods
                    if name in ('self', 'cls'):
                        continue
                    cache_key_parts.append(f"{name}={value}")
                cache_key = ":".join(cache_key_parts)

                # Try to get data from cache
                cached_data = await self.redis.get(cache_key)
                if cached_data:
                    # Assuming cached data is JSON-encoded
                    return_type = func.__annotations__.get('return')
                    if hasattr(return_type, '__origin__') and return_type.__origin__ is list and issubclass(return_type.__args__[0], BaseModel):
                        # Handle List[PydanticModel]
                        item_type = return_type.__args__[0]
                        list_of_dicts = json.loads(cached_data)
                        return [item_type.model_validate(d) for d in list_of_dicts]
                    elif issubclass(return_type, BaseModel): # Pydantic model
                        return return_type.model_validate_json(cached_data)
                    else:
                        return json.loads(cached_data)

                # If not in cache, call the original function
                result = await func(*args, **kwargs)

                # Cache the result
                if isinstance(result, BaseModel): # Pydantic model
                    await self.redis.setex(cache_key, ttl, result.model_dump_json())
                elif isinstance(result, list) and result and isinstance(result[0], BaseModel): # List of Pydantic models
                    await self.redis.setex(cache_key, ttl, json.dumps([item.model_dump() for item in result]))
                elif isinstance(result, (dict, list)):
                    await self.redis.setex(cache_key, ttl, json.dumps(result))
                else:
                    # For other types, convert to string or handle as appropriate
                    await self.redis.setex(cache_key, ttl, str(result)) # Basic string conversion

                return result
            return wrapper
        return decorator

