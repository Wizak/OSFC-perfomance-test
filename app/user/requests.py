import aiohttp
import asyncio
import json
import time

from ..server.config import  CommonRequest, HostServer, CustomStore


def get_users_requests_data(file_path):
    with open(file_path, 'r') as file:
        users_requests = json.load(file)
    users_requests_data = []
    for email, requests_data in users_requests.items():
        for req_data in requests_data:
            new_request_data = {**req_data, "token": CustomStore.users_credentials[email]["token"]}
            users_requests_data.append(new_request_data)
    return users_requests_data
            

async def user_get_request(session, user_request_data):
    request_url = CommonRequest.get_url(user_request_data["endpoint"], user_request_data["querystring"])
    request_headers = CommonRequest.get_headers(user_request_data["token"])
    async with session.get(request_url, headers=request_headers, ssl=HostServer.ssl) as response:
        status_code = response.status
        res_text = await response.text()
        return status_code, json.loads(res_text)


async def bulk_users_requests(users_requests_data, handle_results):
    async with aiohttp.ClientSession() as session:
        users_requests = [user_get_request(session, user_request) for user_request in users_requests_data]
        users_responses = await asyncio.gather(*users_requests)
        handle_results(users_responses)


def run_bulk_users_requests(users_reqeusts_data_file_path, handle_results):
    users_requests_data = get_users_requests_data(users_reqeusts_data_file_path)
    start_time = time.time()
    asyncio.run(bulk_users_requests(users_requests_data, handle_results))
    end_time = time.time()
    CustomStore.users_works_time["bulk_requests"] = abs(start_time - end_time)
    return True