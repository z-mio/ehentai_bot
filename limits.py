import asyncio
from collections import defaultdict
from aiolimiter import AsyncLimiter

MAX_REQUESTS_PER_MINUTE_USER = 3
MAX_REQUESTS_PER_MINUTE_GLOBAL = 30 #其实可以写到conf里面，但是反正后面写队列就先凑合用吧（

user_limiters = defaultdict(lambda: AsyncLimiter(MAX_REQUESTS_PER_MINUTE_USER, time_period=60))
global_limiter = AsyncLimiter(MAX_REQUESTS_PER_MINUTE_GLOBAL, time_period=60)
user_locks = defaultdict(asyncio.Lock)
