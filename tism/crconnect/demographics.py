# -*- coding: utf-8 -*-

from typing import Optional, TypedDict
from requests import Session
from strenum import PascalCaseStrEnum
from . import base
from enum import auto

class Range(TypedDict):
    lower: int
    """The lower bound of the range."""

    upper: int
    """The upper bound of the range including the value itself."""

class DemographicQuota(TypedDict, total=False):
    demographicId: Optional[str]
    demographicOptionIds: Optional[list[str]]
    """
    List of demographic options where targeted participants must have one of the requirements in the list.
    This option is required for single and multiple choice questions."""

    rangeRequirements: Optional[Range]
    """When using a demographic that requires a range of values, this is the range that is required."""

    target: int
    """How many participants are being targeted for this demographic requirement."""

class TargetOption(PascalCaseStrEnum):
    GENERAL_POPULATION = 'GenPop'
    """Open to everyone without any targeting criteria."""

    GENDER_SPLIT = auto()
    """Targets a breakdown between gender."""

    CENSUS_MATCHED = auto()
    """Target a Census matched template."""
    
    CUSTOM = auto()

class DemographicRequirements(TypedDict, total=False):
    quotas: Optional[list[DemographicQuota]]
    """The demographics that will be used to target participants eligible to take part in the project."""

class DemographicTargeting(TypedDict, total=False):
    targetOption: TargetOption
    """The Demographic targeting option you want to use for your project."""

    locations: Optional[list[str]]
    """
    The locations where participants are allowed to complete your project from.
    
    See [Supported Locations](https://connect-api.cloudresearch.com/docs/api/index.html#section/Supported-Locations)
    for possible values.
    """

    languages: Optional[list[str]]
    """
    The languages participants will need to know to complete your Project.
    
    See [Supported Languages](https://connect-api.cloudresearch.com/docs/api/index.html#section/Supported-Languages)
    for possible values.
    """

    demographicRequirements: Optional[DemographicRequirements]
    """Demographic requirements for the project to target a specific audience."""

class DemographicOption(TypedDict, total=False):
    demographicOptionId: Optional[str]
    """Demographic option id that will be needed to be included when creating targeting criteria."""

    value: Optional[str]
    """The specific option that was presented to the participants."""

class DemographicsData(TypedDict, total=False):
    demographicId: Optional[str]
    """Demographic Id that will be needed to be included when creating targeting criteria."""

    question: Optional[str]
    """The question that was asked to the participants."""
    
    category: Optional[str]
    """The category of the demographic."""

    options: Optional[list[DemographicOption]]
    """For single and multiple choice questions, the options that were presented to the participants."""
    
    rangeRequirements: Optional[Range]
    """When using a demographic that requires a range of values, this is the range that is required."""

class DemographicsResponse(TypedDict):
    demographics: Optional[list[DemographicsData]]
    """Demographics that can be used to target a specific audience."""

class FeasibilityRequest(TypedDict, total=False):
    estimatedTimeInMinutes: int
    """How long in minutes you estimate a participant to complete your project."""

    participants: int
    """The amount of participants."""

    payment: float
    """The amount in USD that you will pay."""

    targetingCriteria: Optional[DemographicTargeting]
    """Custom criteria for targeting participants."""

class Platform(PascalCaseStrEnum):
    CONNECT = auto()
    MANAGED_RESEARCH = auto()

class FeasibilityResponse(TypedDict):
    totalProjectCost: float
    """Total cost of the project. Null if the project is not feasible."""

    availablePlatforms: Optional[list[Platform]]


def list_all(session: Optional[Session] = None, **kwargs) -> DemographicsResponse:
    """
    List the demographics that you can use for targeting criteria.
    
    Args:
        session: The current Requests session. If `None`, use the last session that was created
        by `base.create_session()`.
        kwargs: Additional arguments to be passed to `session.request()`.
    
    Returns:
        A list of demographics.
    
    Raises:
        ApiError:
            400 - Bad Request.
            401 - Invalid API or unauthorized resource access.

    """
    return base.get("/demographics/list", session, **kwargs)

def calc_feasibility(data: FeasibilityRequest, session: Optional[Session] = None, idempotency_token: Optional[str] = None, **kwargs) -> FeasibilityResponse:
    """
    Calculate the feasibility for a project.
    
    Args:
        data: Parameters used to calculate feasibility for a project.
        session: The current Requests session. If `None`, use the last session that was created
        by `base.create_session()`.
        idempotency_token: A string used to identify this particular request to prevent duplicates.
        kwargs: Additional arguments to be passed to `session.request()`.

    Returns:
        Feasibility information related to the project.
    
    Raises:
        ApiError:
            400 - Bad Request.
            401 - Invalid API or unauthorized resource access.

    """
    return base.post("/demographics/feasibility", json=data, session=session, idempotency_token=idempotency_token, **kwargs)
