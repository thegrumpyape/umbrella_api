import json
import logging
from typing import List
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from umbrella_api.resources import DestinationList, Destination
from umbrella_api.utils import create_dict_from_kwargs
from umbrella_api.adapter import RestAdapter


class UmbrellaAPI:
    DEFAULT_OPTIONS = {"server": "https://api.umbrella.com", "version": "v2"}

    def __init__(self, ident: str, secret: str, logger: logging.Logger = None):
        self._options = UmbrellaAPI.DEFAULT_OPTIONS
        self._logger = logger or logging.getLogger(__name__)
        self._create_session(ident, secret)
        self._adapter = RestAdapter(self._options, self._session, self._logger)

    def destination_lists(self, expand: bool = False) -> List[DestinationList]:
        r_json = self._page("policies", "destinationlists")
        destination_lists = [
            DestinationList(raw_dl, self._adapter) for raw_dl in r_json
        ]
        if expand:
            for destination_list in destination_lists:
                destinations = self.destinations(destination_list.id)
                setattr(destination_list, "destinations", destinations)
            return destination_lists
        else:
            return destination_lists

    def destination_list(self, id: int, expand: bool = False) -> DestinationList:
        r = self._adapter.get("policies", f"destinationlists/{id}")
        dl = DestinationList(r.data["data"], self._adapter)
        self._logger.info(
            msg=f"message=loaded destination list, id={dl.id}, name={dl.name}, access={dl.access}"
        )
        if expand:
            destinations = self.destinations(dl.id)
            setattr(dl, "destinations", destinations)
            self._logger.info(
                msg=f"message=loaded {len(destinations)} destinations, id={dl.id}, name={dl.name}, access={dl.access}"
            )
            return dl
        else:
            return dl

    def create_destination_list(
        self, name: str, access: str, is_global: bool = False
    ) -> DestinationList:
        data = create_dict_from_kwargs(name=name, access=access, isGlobal=is_global)
        r = self._adapter.post("policies", "destinationlists", data=data)
        dl = DestinationList(r.data, self._adapter)
        self._logger.info(
            msg=f"message=created destination list, id={dl.id}, name={dl.name}, access={dl.access}"
        )
        return dl

    def destinations(self, dl_id: int) -> List[Destination]:
        r_json = self._page("policies", f"destinationlists/{dl_id}/destinations")
        destinations = [
            Destination(raw_dest, self._adapter)
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
            r = self._adapter.get(use_case=use_case, path=path, ep_params=params)
            results.extend(r.data["data"])
            if not r.data["data"]:
                break
            page += 1
        return results
