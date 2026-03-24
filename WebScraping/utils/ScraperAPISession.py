import requests
from scholarly import scholarly

class ScraperAPISession(requests.Session):
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.base_url = "http://api.scraperapi.com"

    def request(self, method, url, *args, **kwargs):
        params = kwargs.get('params', {})
        params.update({
            'api_key': self.api_key,
            'url': url,
            'render': 'true'   

        })
        kwargs['params'] = params

        new_url = self.base_url

        return super().request(method, new_url, *args, **kwargs)

