import json
from umbrella_api.exceptions import raise_on_error, validate_input
from umbrella_api.utils import get_url, create_dict_from_kwargs


class Resource:
    def __init__(self, raw, options, session):
        self._options = options
        self._session = session
        self._parse_raw(raw)

    def _parse_raw(self, raw):
        self.raw = raw
        dict2obj(raw, self)


class Destination(Resource):
    def __init__(self, raw, options, session):
        Resource.__init__(self, raw, options, session)


class DestinationList(Resource):
    def __init__(self, raw, options, session):
        Resource.__init__(self, raw, options, session)

    def update(self, name):
        data = create_dict_from_kwargs(name=name)
        url = get_url(self._options, "policies", f"destinationlists/{self.id}")
        r = self._session.patch(url, json=data)
        raise_on_error(r)
        self._parse_raw(json.loads(r.text)["data"])
        return r.status_code

    # Maybe implement this if a use case is found
    def delete(self):
        pass

    def add_destinations(
        self, destinations: list, type: str = None, comment: str = None
    ):
        data = []
        if validate_input(destinations, list):
            for dest in destinations:
                dest_dict = create_dict_from_kwargs(
                    destination=dest, type=type, comment=comment
                )
                data.append(dest_dict)

        url = get_url(
            self._options, "policies", f"destinationlists/{self.id}/destinations"
        )
        self._chunk_request("POST", url, data, 500)

    def delete_destinations(self, destination_ids: list):
        validate_input(destination_ids, list)
        url = get_url(
            self._options, "policies", f"destinationlists/{self.id}/destinations/remove"
        )
        self._chunk_request("DELETE", url, destination_ids, 500)

    def _chunk_request(
        self, http_method: str, url: str, data: list, chunk_size: int = 500
    ):
        for i in range(0, len(data), chunk_size):
            chunk = data[i : i + chunk_size]
            r = self._session.request(http_method, url, json=chunk)
            raise_on_error(r)
            self._parse_raw(json.loads(r.text)["data"])


def dict2obj(raw, top=None):
    if top is None:
        top = type("PropertyHolder", (object,), raw)

    seqs = tuple, list, set, frozenset
    for i, j in raw.items():
        if isinstance(j, dict):
            setattr(top, i, dict2obj(j))
        elif isinstance(j, seqs):
            seq_list = []
            for seq_elem in j:
                if isinstance(seq_elem, dict):
                    seq_list.append(dict2obj(seq_elem))
                else:
                    seq_list.append(seq_elem)
            setattr(top, i, seq_list)
        else:
            setattr(top, i, j)
    return top
