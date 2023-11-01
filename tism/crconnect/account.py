# -*- coding: utf-8 -*-

from requests import Session
from decimal import Decimal
from typing import TypedDict, Optional
from typing_extensions import Required
from . import base

class AccountInfo(TypedDict):
    accountBalance: Required[Decimal]
    """The available balance that is left in your account."""

def get_info(session: Optional[Session]=None, **kwargs) -> AccountInfo:
    """
    Retrieve account information.

    Args:
        session: The Requests session to use for the base. If `None`, use the last session that was created
        by `base.create_session()`.
        kwargs: Additional arguments to be passed to `session.request()`.

    Raises:
        ApiError:
            400 - Bad Request.
            401 - Invalid API key or unauthorized resource access.
    """
    return base.get("/account", session=session, **kwargs)