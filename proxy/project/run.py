import os
import sys
import logging
from urllib.parse import urljoin
from datetime import datetime
import time
import calendar

import asyncio
from aiohttp import web, ClientSession

import jwt

from redis import Redis
from redis.exceptions import ConnectionError


REDIS_URL = os.environ.get('REDIS_URL', 'localhost')

PROXY_TARGET = os.getenv('PROXY_TARGET', 'https://reqres.in/')

JWT_SECRET = os.getenv(
    'JWT_SECRET',
    'a9ddbcaba8c0ac1a0a812dc0c2f08514b23f2db0a68343cb8199ebb38a6d91e4ebfb378e22ad39c2d01 d0b4ec9c34aa91056862ddace3fbbd6852ee60c36acbf'
)
JWT_ALG = os.getenv('JWT_ALG', 'HS512')
JWT_HEADER = os.getenv('JWT_HEADER', 'x-my-jwt')

HTTP_PORT = 9000

logger = logging.getLogger("proxy")
start_time = time.time()


def get_jwt():
    sjwt = get_bjwt()
    return sjwt.decode()


def get_bjwt():
    timestamp = calendar.timegm(datetime.today().timetuple())
    this = jwt.encode(
        payload={"user": "username", "date": timestamp},
        key=JWT_SECRET,
        algorithm=JWT_ALG,
    )
    logger.info(f'JWT generated on date {datetime.today()} with user username and timespamp {timestamp}')
    return this


def inc_requests_count():
    count = get_requests_count()
    r = Redis(REDIS_URL)
    try:
        r.set('count', count + 1)
    except ConnectionError:
        pass


def get_requests_count():
    r = Redis(REDIS_URL)
    try:
        count = r.get('count')
    except ConnectionError:
        count = 0
    return count


def get_uptime():
    global start_time
    return time.time() - start_time


def render_status():
    return f'response counts {get_requests_count()}. uptime {get_uptime()} sec'


async def handler(request):
    logger.info(f'handled {request.rel_url}')

    if str(request.rel_url).lower().strip('/') == 'status':
        return web.Response(text=render_status(), status=200)

    async with ClientSession() as session:
        async with session.get(urljoin(PROXY_TARGET, str(request.rel_url))) as resp:
            text = await resp.text()

    headers = {}
    jwt_header_text = get_jwt()
    if jwt:
        headers[JWT_HEADER] = jwt_header_text

    inc_requests_count()

    return web.Response(text=text, headers=headers, status=resp.status)


async def proxy():
    server = web.Server(handler)
    runner = web.ServerRunner(server)
    await runner.setup()
    site = web.TCPSite(runner)
    await site.start()

    print("======= Serving on http://localhost/ =======")

    # pause here for very long time by serving HTTP requests and
    # waiting for keyboard interruption
    await asyncio.sleep(100*3600)


def run():
    logging.root.setLevel(logging.INFO)
    logging.root.addHandler(logging.StreamHandler(sys.stdout))

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(proxy())
    except KeyboardInterrupt:
        pass
    loop.close()
