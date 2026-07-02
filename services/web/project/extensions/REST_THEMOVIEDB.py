import json
from re import I
import time
import requests
from requests.models import Response
import logging
import urllib3
from requests.auth import HTTPBasicAuth
from .. import app, log
from datetime import datetime


from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


THEMOVIEDB_API_VERSION = app.config['THEMOVIEDB_API_VERSION']
HEADERS = app.config['THEMOVIEDB_HEADERS']

class RequestDebugDecorator(object):
    def __init__(self, action):
        self.action = action

    def __call__(self, f):
        def wrapped_f(*args):
            action = self.action
            logger = args[0].logger
            request = args[1]
            start_time = time.time()
            logger.debug('{0}: {1}'.format(action, request))
            result = f(*args)
            status_code = result.status_code
            time_used = time.time() - start_time
            logger.debug('Response Code: {0} ({1}: {2}) [{3}]'.format(status_code, action, request, time_used))
            if status_code >= 400:
                logger.debug('Error: {0}'.format(result.content))
            return result

        return wrapped_f


class RESTTheMovieDB(object):
    def __init__(self, hostname=None , api_key=None,
        protocol='https', verify_cert=False, logger = None, timeout=120):
        """
        """
        self.logger = self._get_logger(logger)
        self.hostname = hostname
        self.api_key = api_key
        self.protocol = protocol
        self.verify_cert = verify_cert
        self.timeout = timeout

    @staticmethod
    def _get_logger(logger):
        """
        """
        if not logger:
            dummy_logger = logging.getLogger('REST_API')
            dummy_logger.addHandler(logging.NullHandler())
            return dummy_logger
        return logger

    def _url(self, path=''):
        """
        """
        return '{0}://{1}{2}{3}'.format(self.protocol , self.hostname, THEMOVIEDB_API_VERSION, path)



    def _get_request(self, request, params=dict()):
        """
        """
        params['api_key'] = self.api_key
        try:
            response = requests.get(request, headers=HEADERS, params=params , verify=self.verify_cert, timeout=self.timeout)
        except requests.exceptions.RequestException as e:
            log.error(e)

        return response

    def _get(self, request, params=dict()):
        """
        """
        responses = list()
        response = self._get_request(request, params)
        
        responses.append(response)
        payload = response.json()

        if 'page' in payload.keys() and 'total_pages' in payload.keys():
            page = int(payload['page'])
            total_pages = int(payload['total_pages'])
            if page < total_pages:
                for i in range(page +1, total_pages +1):
                    params['page'] = i
                    response_page = self._get_request(request,params)
                    responses.append(response_page)
        return responses


    def get_movies(self):
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        path = '/discover/movie'
        params = {
            # 'primary_release_date.gte': app.config['PRIMARY_RELEASE_DATE_GTE'],
            'primary_release_date.gte': today,
            'primary_release_date.lte': today,
            }
        url = self._url(path)
        return self._get(url, params)

    def get_genres_for_movie(self):
        path = '/genre/movie/list'
        url = self._url( path)
        return self._get(url)