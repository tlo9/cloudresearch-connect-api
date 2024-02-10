# -*- coding: utf-8 -*-

import requests
from requests import Session
from typing import Iterator, Mapping, Optional, Any, TypedDict
from typing_extensions import override

BASE_URL = 'https://connect-api.cloudresearch.com'

CURRENT_SESSION: Optional[Session] = None

class SessionException(Exception):
    pass

class ApiErrorData(TypedDict):
    type: Optional[str]
    title: Optional[str]
    status: Optional[int]
    detail: Optional[str]
    instance: Optional[str]

class ApiError(Exception):
    '''Encapsulate an error response due to sending an API base.
    
    Attributes:
        status_code: The HTTP status code for the error.
        data: The JSON content body of the error.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = args[0]

        match args[1]:
            case { 'error': error_data }:
                self.data: Optional[ApiErrorData] = error_data
            case _:
                self.data = None

def _to_query_str(query_dict: Mapping[Any, Any], acc: Optional[str] = None) -> Iterator:
    for (key, value) in query_dict.items():
        match value:
            case dict() if acc is None:
                yield '&'.join(_to_query_str(value, str(key)))
            case dict() if acc is not None:
                yield '&'.join(_to_query_str(value, f"{acc}[{str(key)}]"))
            case _ if acc is None:
                yield f"{str(key)}={str(value)}"
            case _ if acc is not None:
                yield f"{acc}[{str(key)}]={str(value)}"

def to_query_str(query_dict: Mapping[Any, Any]) -> str:
    '''
    Convert a dict of values into a query string.
    
    This also handles nested dicts by enclosing nested key names in square brackets.
    
    For example, `team[employee][name]=Scott` would be the result of converting the following `dict`:
    
    >>> { 'team': { 'employee': { 'name': 'Scott' } } }

    Note: This assumes that the `str` representation of the keys and values of the `dict` only contain
    URL-safe characters.

    Args:
        query_dict: A `dict` of key/value pairs. Both the key and the value must be able
        to be represented as a `str`.
    
    Returns:
        A query string.
    '''
    return '&'.join(_to_query_str(query_dict))

def endpoint_url(path: str, version: str = 'v1', query: Optional[str | Mapping[Any, Any]] = None) -> str:
    '''
    Build an endpoint URL string from an endpoint path.
    
    Args:
        path: The endpoint path (not including the base url).
        version: The API version to use (default: `v1`).
        query: An optional url query. It may be a query string or a `dict` of key value pairs.
    
    Returns:
        An endpoint URL `str`.
    '''

    # FIXME: path and query should be cleaned/validated to ensure that they can form a valid URL.

    match query:
        case str():
            return f"{BASE_URL}/api/{version}{path}?{query}"
        case { **queries }:
            return f"{BASE_URL}/api/{version}{path}?{to_query_str(queries)}"
        case _:
            return f"{BASE_URL}/api/{version}{path}"

def create_session(api_key: str, set_current_session: bool = True) -> Session:
    '''
    Create a new Requests session that uses an api key for all subsequent requests.
    
    Each API call must be associated with a valid API key. A session allows one to save
    the key and have it persist across multiple requests.

    Args:
        api_key: The CloudResearch Connect API key.
        set_current_session: If `True` the current session will be replaced with the newly created one.
    
    Returns:
        A Requests session.
    '''

    # FIXME: This isn't thread-safe

    global CURRENT_SESSION

    s = requests.session()
    s.headers['X-API-KEY'] = api_key
    
    if set_current_session:
        CURRENT_SESSION = s
    
    return s

def request(method: str, path: str, query: Optional[str | Mapping[Any, Any]] = None,
            json_response: bool = True, return_response: bool = False, idempotency_token: Optional[str] = None,
            session: Optional[Session] = None, **kwargs) -> Any:
    '''
    Perform an API request and return the JSON response as a `dict`.
    
    Args:
        method: The HTTP verb (e.g. GET, POST, PUT, etc.)
        path: The endpoint path (not including the base url).
        query: An optional url query. It may be a query string or a `dict` of key/value pairs.
        json_response: Return the response as a JSON `dict` if True, otherwise return `bytes`.
        return_response: Return the Requests response itself instead of the content body.
        idempotency_token: A string used to identify this particular request to prevent duplicates.
        session: The current Requests session. If `None`, then the most recent session created by `create_session()` is used.
        kwargs: Additional arguments to be passed to `session.request()`.
    
    Returns:
        If `return_response = True`, a Requests response (regardless of the value of `json_response`).
        If `return_response = False`, the content of response as a JSON parsed `dict`
        if `json_response` is `True`, otherwise a sequence of `bytes`.
    
    Raises:
        SessionException: `session=None` and `create_session()` was not called.
        ApiError: A 4xx or 5xx HTTP response was received along with error information.
    '''

    if session is None:
        if CURRENT_SESSION is None:
            raise SessionException("No session has been supplied. Either use create_session() or a Requests Session object.")
        else:
            session = CURRENT_SESSION

    response = session.request(
        headers=({ 'IDEMPOTENCY-TOKEN': idempotency_token } if idempotency_token is not None else {}),
        method=method,
        url=endpoint_url(path, query=query),
        **kwargs,
        )
    
    if response.ok:
        if return_response:
            return response
        elif json_response:
            return response.json()
        else:
            return response.content
    else:
        raise ApiError(response.status_code, response.json())

def get(path: str, query: Optional[str | dict[Any, Any]] = None, session: Optional[Session] = None,
        json_response: bool = True, return_response: bool = False, **kwargs) -> Any:
    '''
    Perform a GET request and return the content of the response.
    
    Args:
        path: The endpoint path (not including the base url).
        query: An optional url query. It may be a query string or a `dict` of key/value pairs.
        session: The current Requests session. If `None`, then the most recent session created by `create_session()` is used.
        json_response: Return the response as a JSON `dict` if True, otherwise return `bytes`.
        return_response: Return the Requests response itself instead of the content body.
        kwargs: Additional arguments to be passed to `session.request()`.
    
    Returns:
        The content of response as a JSON parsed `dict` if `json_response` is `True`, otherwise a
        sequence of `bytes`.
    
    Raises:
        ApiError: A 4xx or 5xx HTTP response was received along with error information.
    '''

    return request('GET', path, query, json_response=json_response, return_response=return_response,
                   session=session, **kwargs)

def post(path: str, query: Optional[str | dict[Any, Any]] = None, session: Optional[Session] = None,
         idempotency_token: Optional[str] = None, json_response: bool = True, return_response: bool = False, **kwargs) -> Any:
    '''
    Perform a POST request and return the content of the response.
    
    Args:
        path: The endpoint path (not including the base url).
        query: An optional url query. It may be a query string or a `dict` of key/value pairs.
        session: The current Requests session. If `None`, then the most recent session created by `create_session()` is used.
        idempotency_token: A string used to identify this particular request to prevent duplicates.
        json_response: Return the response as a JSON `dict` if True, otherwise return `bytes`.
        return_response: Return the Requests response itself instead of the content body.
        **kwargs: Additional arguments to be passed to `session.request()`.
    
    Returns:
        The JSON response as a `dict`.
    
    Raises:
        ApiError: A 4xx or 5xx HTTP response was received along with error information.
    '''

    return request('POST', path, query, idempotency_token=idempotency_token,
                   json_response=json_response, return_response=return_response, session=session,
                   **kwargs)

def delete(path: str, query: Optional[str | dict[Any, Any]] = None, session: Optional[Session] = None,
           idempotency_token: Optional[str] = None, json_response: bool = True, return_response: bool = False, **kwargs) -> Any:
    '''
    Perform a DELETE request and return the content of the response.
    
    Args:
        path: The endpoint path (not including the base url).
        query: An optional url query. It may be a query string or a `dict` of key/value pairs.
        session: The current Requests session. If `None`, then the most recent session created by `create_session()` is used.
        idempotency_token: A string used to identify this particular request to prevent duplicates.
        json_response: Return the response as a JSON `dict` if True, otherwise return `bytes`.
        return_response: Return the Requests response itself instead of the content body.
        kwargs: Additional arguments to be passed to `session.request()`.
    
    Returns:
        The JSON response as a `dict`.
    
    Raises:
        ApiError: A 4xx or 5xx HTTP response was received along with error information.
    '''

    return request('DELETE', path, query, idempotency_token=idempotency_token,
                   json_response=json_response, return_response=return_response, session=session,
                   **kwargs)

def put(path: str, query: Optional[str | dict[Any, Any]] = None, session: Optional[Session] = None,
        idempotency_token: Optional[str] = None, json_response: bool = True, return_response: bool = False, **kwargs) -> Any:
    '''
    Perform a PUT request and return the content of the response.
    
    Args:
        path: The endpoint path (not including the base url).
        query: An optional url query. It may be a query string or a `dict` of key/value pairs.
        session: The current Requests session. If `None`, then the most recent session created by `create_session()` is used.
        idempotency_token: A string used to identify this particular request to prevent duplicates.
        json_response: Return the response as a JSON `dict` if True, otherwise return `bytes`.
        return_response: Return the Requests response itself instead of the content body.
        kwargs: Additional arguments to be passed to `session.request()`.
    
    Returns:
        The JSON response as a `dict`.
    
    Raises:
        ApiError: A 4xx or 5xx HTTP response was received along with error information.
    '''

    return request('PUT', path, query, idempotency_token=idempotency_token,
                   json_response=json_response, return_response=return_response, session=session,
                   **kwargs)

def patch(path: str, query: Optional[str | dict[Any, Any]] = None, session: Optional[Session] = None,
          idempotency_token: Optional[str] = None, json_response: bool = True, return_response: bool = False, **kwargs) -> Any:
    '''
    Perform a PATCH request and return the content of the response.
    
    Args:
        path: The endpoint path (not including the base url).
        query: An optional url query. It may be a query string or a `dict` of key/value pairs.
        session: The current Requests session. If `None`, then the most recent session created by `create_session()` is used.
        idempotency_token: A string used to identify this particular request to prevent duplicates.
        json_response: Return the response as a JSON `dict` if True, otherwise return `bytes`.
        return_response: Return the Requests response itself instead of the content body.
        kwargs: Additional arguments to be passed to `session.request()`.
    
    Returns:
        The JSON response as a `dict`.
    
    Raises:
        ApiError: A 4xx or 5xx HTTP response was received along with error information.
    '''

    return request('PATCH', path, query, idempotency_token=idempotency_token,
                   json_response=json_response, return_response=return_response, session=session,
                   **kwargs)
