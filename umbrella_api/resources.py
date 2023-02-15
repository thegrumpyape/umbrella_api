from typing import Dict
from umbrella_api.exceptions import validate_input
from umbrella_api.utils import create_dict_from_kwargs, dict2obj
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

    def update(self, name: str) -> None:
        validate_input(name, str)
        data = create_dict_from_kwargs(name=name)
        r = self._adapter.patch(
            use_case="policies", path=f"destinationlists/{self.id}", data=data
        )
        self._parse_raw(r.data["data"])

    def add_destinations(
        self, destinations: list, type: str = None, comment: str = None
    ) -> None:
        validate_input(destinations, list)
        data = [
            create_dict_from_kwargs(destination=dest, type=type, comment=comment)
            for dest in destinations
        ]
        self._chunk_request(
            http_method="POST",
            use_case="policies",
            path=f"destinationlists/{self.id}/destinations",
            data=data,
            chunk_size=500,
        )

    def delete_destinations(self, destination_ids: list) -> None:
        validate_input(destination_ids, list)
        self._chunk_request(
            http_method="DELETE",
            use_case="policies",
            path=f"destinationlists/{self.id}/destinations/remove",
            data=destination_ids,
            chunk_size=500,
        )

    def _chunk_request(
        self,
        http_method: str,
        use_case: str,
        path: str,
        data: list,
        chunk_size: int = 500,
    ) -> None:
        for i in range(0, len(data), chunk_size):
            chunk = data[i : i + chunk_size]
            r = self._adapter.do(
                http_method=http_method, use_case=use_case, path=path, data=chunk
            )
            self._parse_raw(r.data["data"])
