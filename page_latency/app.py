import json
import time
import asyncio
from aiohttp import ClientSession, client_exceptions, ClientTimeout


def lambda_handler(event, context):
    body = json.loads(event["body"])
    try:
        links = body['links']
    except TypeError as err:
        return {
            'status_code': 500,
            'body': err
        }
    else:
        response = {}
        for site in asyncio.run(links_stack(links)):
            response.update(site)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }


async def links_stack(links):
    async with ClientSession() as session:
        tasks = []
        for link in links:
            tasks.append(define_time(session, link))
        return await asyncio.gather(*tasks)


async def define_time(session, link):
    try:
        page_time = 0
        timeout = ClientTimeout(total=9)
        start = time.time()
        async with await session.get(link, timeout=timeout):
            end = time.time()
            page_time += end - start
        return {link: page_time}
    except client_exceptions.ClientConnectionError:
        return {link: 'Connection Error'}
    except asyncio.exceptions.TimeoutError:
        return {link: 'Timeout Error'}
