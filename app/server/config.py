class HostServer:
    domain = "osfc-test.userlogin.eu"
    port = 8000
    ssl = False

    @classmethod
    def get_address(cls):
        return f'{"https" if cls.ssl else "http"}://{cls.domain}:{cls.port or ""}'.strip(":")


class BaseRequest:
    @classmethod
    def get_url(cls, endpoint="", querystring=""):
        return f'{HostServer.get_address()}/{endpoint}?{querystring}'.strip("?").strip("/")

    @classmethod
    def get_headers(cls, additional_headers):
        return {
            'Accept-Language': 'uk,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Pragma': 'no-cache',
            'Referer': f'{HostServer.get_address()}/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'accept': 'application/json',
            'content-type': 'application/json',
            **additional_headers,
        }


class AuthRequest(BaseRequest):
    @classmethod
    def get_url(cls):
        return BaseRequest.get_url(endpoint="login")

    @classmethod
    def get_headers(cls):
        return BaseRequest.get_headers(additional_headers={
            'Origin': HostServer.get_address(),
            'authorization': 'Bearer null',
        })


class CommonRequest(BaseRequest):
    @classmethod
    def get_url(cls, endpoint, querystring):
        return BaseRequest.get_url(endpoint=endpoint, querystring=querystring)

    @classmethod
    def get_headers(cls, token):
        return BaseRequest.get_headers(additional_headers={
            'authorization': f'Bearer {token}',
        })


class CustomStore:
    users_credentials = dict()
    users_works_time = dict()