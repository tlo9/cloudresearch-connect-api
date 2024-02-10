# -*- coding: utf-8 -*-

"""
After a participant completes their assignment, their assignment status will be in a `Pending` state.
Researchers will have 14 days to either `Approve` or `Reject` the work that the participant has submitted.
If a participant's assignment is not approved within 14 days of the completion time of the assignment, the
assignment will be automatically be approved.

A `Pending` assignment can be either `Approved` or `Rejected`. However, once a assignment is `Approved`, you
will no longer be able to reject the participant. A `Rejected` assignment on the other hand, can be `Approved`
even after it has been `Rejected`.

If assignments are `Rejected`, your account balance will be credited with the amount that would have paid to
the participants plus any associated Connect fees.
"""

from enum import auto
from typing import Optional, TypedDict

from requests import Session
from strenum import PascalCaseStrEnum
from . import base

class SubmissionType(PascalCaseStrEnum):
    COMPLETION_CODE = auto()
    REDIRECT = auto()

class CompletionInfo(TypedDict):
    completionCode: Optional[str]
    """
    The code the participant submitted when completing the Project or `null` if
    completed using a redirect link.
    """

    submissionType: SubmissionType
    """The submission method used by the participant to complete the project."""

class AssignmentStatus(PascalCaseStrEnum):
    PENDING = auto()
    APPROVED = auto()
    REJECTED = auto()

class Assignment(TypedDict):
    participantId: Optional[str]
    """The id of the participant."""

    assignmentId: Optional[str]

    startTime: str
    """When the participant started the project."""

    completionTime: Optional[str]
    """When the participant completed the project."""

    status: AssignmentStatus
    """The status of the assignments."""

    payment: float
    """The amount in USD that you will pay."""

    bonus: float
    """How much the participant has been bonused for this project."""

    completion: CompletionInfo
    """Information on how the participant submitted the project."""


class AssignmentResponse(TypedDict):
    assignments: Optional[list[Assignment]]

class Participant(TypedDict, total=False):
    id: Optional[str]
    """The participant or assignment id to approve or reject."""

    message: Optional[str]
    """The message to display to the participant."""

class BonusPayment(TypedDict, total=False):
    id: Optional[str]
    """The ID of the participant or assignment."""

    message: Optional[str]
    """The message to display to the participant."""

    amount: float
    """The amount to bonus."""

def list_all(project_id: str, session: Optional[Session] = None, **kwargs) -> AssignmentResponse:
    """
    List all assignments for a project.

    Args:
        project_id: The project ID.
        session: The current Requests session. If `None`, use the last session that was created
        by `base.create_session()`.
        kwargs: Additional arguments to be passed to `session.request()`.

    Returns:
        A list of assignments.
    
    Raises:
        ApiError:
            400 - Bad Request.
            401 - Invalid API or unauthorized resource access.
    """
    return base.get(f'/assignments/{project_id}', session=session, **kwargs)

def approve(project_id: str, participants: list[Participant], session: Optional[Session] = None, idempotency_token: Optional[str]=None, **kwargs) -> None:
    """
    Approve participants associated with a project.

    Args:
        project_id: The project ID.
        participants: A list of participant IDs and feedback messages (must not be empty).
        session: The current Requests session. If `None`, use the last session that was created
        by `base.create_session()`.
        idempotency_token: A string used to identify this particular request to prevent duplicates.
        kwargs: Additional arguments to be passed to `session.request()`.

    Raises:
        ApiError:
            400 - Bad Request.
            401 - Invalid API or unauthorized resource access.
    """
    base.post(f"/assignments/{project_id}/approve",
                 json={
                     'participants': participants
                 },
                 session=session,
                 idempotency_token=idempotency_token,
                 json_response=False,
                 **kwargs)

def approve_all(project_id: str, message: Optional[str]=None, session: Optional[Session] = None, idempotency_token: Optional[str]=None, **kwargs) -> None:
    """
    Approve all participants associated with a project.

    Args:
        project_id: The project ID.
        message: The feedback message to be sent to participants.
        session: The current Requests session. If `None`, use the last session that was created
        by `base.create_session()`.
        idempotency_token: A string used to identify this particular request to prevent duplicates.
        kwargs: Additional arguments to be passed to `session.request()`.

    Raises:
        ApiError:
            400 - Bad Request.
            401 - Invalid API or unauthorized resource access.
    """
    base.post(f"/assignments/{project_id}/approve-all",
                 json={
                     'message': message if message is not None else ''
                 },
                 session=session,
                 idempotency_token=idempotency_token,
                 json_response=False,
                 **kwargs)

def reject(project_id: str, participants: list[Participant], session: Optional[Session] = None, idempotency_token: Optional[str]=None, **kwargs) -> None:
    """
    Reject participants associated with a project

    Every rejected assignment needs to include a message as to why the assignment was rejected.

    Your account balance will be credited with the amount that would have paid to the
    participants plus any associated Connect fees.

    Args:
        project_id: The project ID.
        participants: A list of participant IDs and feedback messages (must not be empty).
        session: The current Requests session. If `None`, use the last session that was created
        by `base.create_session()`.
        idempotency_token: A string used to identify this particular request to prevent duplicates.
        kwargs: Additional arguments to be passed to `session.request()`.

    Raises:
        ApiError:
            400 - Bad Request.
            401 - Invalid API or unauthorized resource access.
    """
    base.post(f"/assignments/{project_id}/reject",
                 json={
                     'participants': participants
                 },
                 session=session,
                 idempotency_token=idempotency_token,
                 json_response=False,
                 **kwargs)

def bonus(project_id: str, bonus_payments: list[BonusPayment], session: Optional[Session] = None, idempotency_token: Optional[str]=None, **kwargs) -> None:
    """
    Bonus participants associated with a project

    You will need to have enough funds in your account for the total amount plus any
    associated Connect fees. If there are insufficient funds, then the bonuses will
    not go through for any of the participants.

    Args:
        project_id: The project ID.
        bonus_payment: A list of bonus payments to be paid to participants.
        session: The current Requests session. If `None`, use the last session that was created
        by `base.create_session()`.
        idempotency_token: A string used to identify this particular request to prevent duplicates.
        kwargs: Additional arguments to be passed to `session.request()`.

    Raises:
        ApiError:
            400 - Bad Request.
            401 - Invalid API or unauthorized resource access.
    """
    base.post(f"/assignments/{project_id}/bonus",
                 json={
                     'bonusPayment': bonus_payments
                 },
                 session=session,
                 idempotency_token=idempotency_token,
                 json_response=False,
                 **kwargs)

def reverse_rejections(project_id: str, participants: list[Participant], session: Optional[Session] = None, idempotency_token: Optional[str]=None, **kwargs) -> None:
    """
    Reverse Rejections for previously Rejected assignments for a project.

    Rejected assignments can be Approved even though they have been previously `Rejected`.
    Once `Approved`, the assignment can no longer be rejected. There must be enough money
    in your account balance to pay these previously `Rejected` participants.

    Args:
        project_id: The project ID.
        participants: A list of participant IDs and feedback messages (must not be empty).
        session: The current Requests session. If `None`, use the last session that was created
        by `base.create_session()`.
        idempotency_token: A string used to identify this particular request to prevent duplicates.
        kwargs: Additional arguments to be passed to `session.request()`.

    Raises:
        ApiError:
            400 - Bad Request.
            401 - Invalid API or unauthorized resource access.
    """
    base.post(f"/assignments/{project_id}/reverse-reject",
                 json={
                     'participants': participants
                 },
                 session=session,
                 idempotency_token=idempotency_token,
                 json_response=False,
                 **kwargs)
