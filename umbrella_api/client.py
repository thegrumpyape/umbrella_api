import json
import logging
from typing import List

from oauthlib.oauth2 import BackendApplicationClient
from oauthlib.oauth2 import TokenExpiredError
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth

from umbrella_api.exceptions import raise_on_error
from umbrella_api.resources import DestinationList, Destination
from umbrella_api.utils import get_url, create_dict_from_kwargs


class UmbrellaAPI:
    DEFAULT_OPTIONS = {"server": "https://api.umbrella.com", "version": "v2"}

    def __init__(self, ident: str, secret: str, logger: logging.Logger = None):
        self._options = UmbrellaAPI.DEFAULT_OPTIONS
        self._logger = logger or logging.getLogger(__name__)
        self._create_session(ident, secret)

    def destination_lists(self, expand: bool = False) -> List[DestinationList]:
        r_json = self._page("policies", "destinationlists")
        destination_lists = [
            DestinationList(raw_dl, self._options, self._session) for raw_dl in r_json
        ]
        if expand:
            for destination_list in destination_lists:
                destinations = self.destinations(destination_list.id)
                setattr(destination_list, "destinations", destinations)
            return destination_lists
        else:
            return destination_lists

    def destination_list(self, id: int, expand: bool = False) -> DestinationList:
        r_json = self._get_json("policies", f"destinationlists/{id}")
        destination_list = DestinationList(r_json, self._options, self._session)
        if expand:
            destinations = self.destinations(destination_list.id)
            setattr(destination_list, "destinations", destinations)
            return destination_list
        else:
            return destination_list

    def create_destination_list(
        self, name: str, access: str, is_global: bool = False
    ) -> DestinationList:
        data = create_dict_from_kwargs(name=name, access=access, isGlobal=is_global)
        url = get_url(self._options, "policies", "destinationlists")
        r = self._session.post(url, json=data)
        raise_on_error(r)
        return DestinationList(json.loads(r.text), self._options, self._session)

    def destinations(self, dl_id: int) -> List[Destination]:
        r_json = self._page("policies", f"destinationlists/{dl_id}/destinations")
        destinations = [
            DestinationList(raw_dest, self._options, self._session)
            for raw_dest in r_json
        ]
        return destinations

    def _create_session(self, ident: str, secret: str) -> None:
        url = "{server}/auth/v2/token".format(**self._options)
        auth = HTTPBasicAuth(ident, secret)
        client = BackendApplicationClient(ident)
        self._session = OAuth2Session(client=client)
        self._session.fetch_token(token_url=url, auth=auth)

    def _page(self, use_case: str, path: str, limit: int = 100, params: dict = None):
        results = []
        page = 1

        if params is None:
            params = {}

        while True:
            params["page"] = page
            params["limit"] = limit
            page_results = self._get_json(use_case, path, params)
            results.extend(page_results)
            if not page_results:
                break
            page += 1
        return results

    def _get_json(self, use_case: str, path: str, params: dict = None) -> json:
        url = get_url(self._options, use_case, path)
        r = self._session.get(url, params=params)
        is_success = raise_on_error(r)
        self._logger.debug(
            msg=f"method=GET, url={url}, params={params}, success={is_success}, status_code={r.status_code}, message={r.reason}"
        )
        r_json = json.loads(r.text)
        return r_json["data"]
