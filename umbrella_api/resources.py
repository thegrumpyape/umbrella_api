from typing import Dict, List
import logging
from umbrella_api.exceptions import validate_input
from umbrella_api.utils import kwargs2dict, dict2obj
from umbrella_api.adapter import RestAdapter


class Resource:
    def __init__(self, raw: Dict, adapter: RestAdapter):
        self._adapter = adapter
        self._parse_raw(raw)

    def _parse_raw(self, raw: Dict):
        self.raw = raw
        dict2obj(raw, self)


class Destination(Resource):
    def __init__(self, raw, adapter: RestAdapter):
        Resource.__init__(self, raw, adapter)


class DestinationList(Resource):
    def __init__(self, raw, adapter: RestAdapter):
        Resource.__init__(self, raw, adapter)
        self.destinations = []

    def update(self, name: str) -> None:
        validate_input(name, str)
        data = kwargs2dict(name=name)
        r = self._adapter.patch(
            use_case="policies", path=f"destinationlists/{self.id}", data=data
        )
        self._parse_raw(r.data["data"])

    def get_destinations(self) -> List[Destination]:
        r_json = self._adapter.page(
            "policies", f"destinationlists/{self.id}/destinations"
        )
        self.destinations += [Destination(raw_dest, self._adapter) for raw_dest in r_json]
        self._adapter._logger.info(
            msg=f"message=loaded {len(self.destinations)} destinations, id={self.id}, name={self.name}, access={self.access}"
        )
        return self.destinations

    def add_destinations(
        self, destinations: list, type: str = None, comment: str = None
    ) -> None:
        validate_input(destinations, list)
        data = [
            kwargs2dict(destination=dest, type=type, comment=comment)
            for dest in destinations
        ]
        self._adapter.chunk(
            http_method="POST",
            use_case="policies",
            path=f"destinationlists/{self.id}/destinations",
            data=data,
            chunk_size=500,
        )

    def delete_destinations(self, destination_ids: list) -> None:
        validate_input(destination_ids, list)
        self._adapter.chunk(
            http_method="DELETE",
            use_case="policies",
            path=f"destinationlists/{self.id}/destinations/remove",
            data=destination_ids,
            chunk_size=500,
        )
