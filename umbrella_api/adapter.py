import json
import logging
from typing import Dict, List
from requests import Session
from umbrella_api.exceptions import raise_on_error


class Result:
    def __init__(self, status_code: int, message: str = "", data=None):
        self.status_code = int(status_code)
        self.message = str(message)
        self.data = data


class RestAdapter:
    def __init__(self, options, session: Session, logger: logging.Logger = None):
        self._options = options
        self._session = session
        self._logger = logger or logging.getLogger(__name__)

    def _url(self, use_case, path) -> str:
        return "{}/{}/{}/{}".format(
            self._options["server"], use_case, self._options["version"], path
        )

    def do(
        self,
        http_method: str,
        use_case: str,
        path: str,
        ep_params: Dict = None,
        data: Dict = None,
    ) -> Result:
        url = self._url(use_case, path)
        r = self._session.request(
            method=http_method, url=url, params=ep_params, json=data
        )
        is_success = 299 >= r.status_code >= 200  # 200 to 299 is OK
        log_line = f"method={http_method}, url={url}, headers={self._session.headers}, params={ep_params}, success={is_success}, status_code={r.status_code}, message={r.reason}"
        if is_success:
            self._logger.debug(msg=log_line)
            return Result(r.status_code, message=r.reason, data=json.loads(r.text))
        self._logger.error(msg=log_line)
        raise_on_error(r)

    def get(self, use_case: str, path: str, ep_params: Dict = None) -> Result:
        return self.do(
            http_method="GET", use_case=use_case, path=path, ep_params=ep_params
        )

    def post(
        self, use_case: str, path: str, ep_params: Dict = None, data: Dict = None
    ) -> Result:
        return self.do(
            http_method="POST",
            use_case=use_case,
            path=path,
            ep_params=ep_params,
            data=data,
        )

    def delete(
        self, use_case: str, path: str, ep_params: Dict = None, data: Dict = None
    ) -> Result:
        return self.do(
            http_method="DELETE",
            use_case=use_case,
            path=path,
            ep_params=ep_params,
            data=data,
        )

    def patch(
        self, use_case: str, path: str, ep_params: Dict = None, data: Dict = None
    ) -> Result:
        return self.do(
            http_method="PATCH",
            use_case=use_case,
            path=path,
            ep_params=ep_params,
            data=data,
        )

    def page(
        self, use_case: str, path: str, page_size: int = 100, params: dict = None
    ) -> List:
        results = []
        page = 1

        if params is None:
            params = {}

        while True:
            params["page"] = page
            params["limit"] = page_size
            r = self.get(use_case=use_case, path=path, ep_params=params)
            results.extend(r.data["data"])
            if not r.data["data"]:
                break
            page += 1
        return results

    def chunk(
        self,
        http_method: str,
        use_case: str,
        path: str,
        data: list,
        chunk_size: int = 500,
    ) -> None:
        for i in range(0, len(data), chunk_size):
            chunk = data[i : i + chunk_size]
            r = self.do(
                http_method=http_method, use_case=use_case, path=path, data=chunk
            )
        return r.data["data"]
