import aiohttp
import asyncio
import json
import time

from ..server.config import AuthRequest, HostServer, CustomStore


async def authorize_user(session, payload):
    async with session.post(AuthRequest.get_url(), headers=AuthRequest.get_headers(), 
                            data=json.dumps(payload), ssl=HostServer.ssl) as response:
        status_code = response.status
        res_text = await response.text()
        return status_code, json.loads(res_text)


async def bulk_authorization(users_data, handle_results):
    async with aiohttp.ClientSession() as session:
        authorization_requests = [authorize_user(session, user_data) for user_data in users_data]
        authorization_responses = await asyncio.gather(*authorization_requests)
        handle_results(authorization_responses)


def run_bulk_authorization(user_data_file_path, handle_results):
    with open(user_data_file_path, 'r') as file:
        users = json.load(file)
    start_time = time.time()
    asyncio.run(bulk_authorization(users, handle_results))
    end_time = time.time()
    CustomStore.users_works_time["bulk_authorization"] = abs(start_time - end_time)
    return True