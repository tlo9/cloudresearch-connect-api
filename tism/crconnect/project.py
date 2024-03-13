# -*- coding: utf-8 -*-

from requests import Session
from typing import TypedDict, Optional
from strenum import PascalCaseStrEnum, StrEnum
from enum import auto
from typing_extensions import Required
from collections.abc import Generator
from . demographics import DemographicTargeting
from . import base

class SystemRequirement(PascalCaseStrEnum):
    AUDIO = auto()
    CAMERA = auto()
    MICROPHONE = auto()
    DOWNLOAD_SOFTWARE = auto()
    WRITING = auto()

class DeviceType(PascalCaseStrEnum):
    DESKTOP = auto()
    TABLET = auto()
    MOBILE = auto()

class ProjectCompletionType(PascalCaseStrEnum):
    REDIRECT_URL = auto()
    COMPLETION_CODE = auto()
    TEMPLATE = auto()

class CompletionSettings(TypedDict, total=False):
    value: Optional[str]
    projectCompletionType: ProjectCompletionType

class Location(StrEnum):
    US = auto()

class Language(StrEnum):
    ENGLISH = 'en'

class ParticipantTargeting(TypedDict, total=False):
    includedParticipants: list[str]
    """The participant ids that should be allowed to take this project."""

    excludedParticipants: list[str]
    """The participant ids that should be prevented from taking this project."""

class ProjectTargeting(TypedDict, total=False):
    includedProjects: list[str]
    """The project ids that participants should be allowed from taking this project."""

    excludedProjects: list[str]
    """The project ids that participants should be excluded from taking this project."""

class PlatformTargeting(TypedDict, total=False):
    participants: Optional[ParticipantTargeting]
    projects: Optional[ProjectTargeting]

class TaskTemplateType(PascalCaseStrEnum):
    DATA_LABELING = auto()
    CUSTOM_HTML = auto()

class TemplateDataCell(TypedDict):
    value: Optional[str]
    '''The value of the cell.'''

class TemplateDataRow(TypedDict):
    cells: Optional[list[TemplateDataCell]]
    """All the data cells."""

class DataLabelingResponseMethod(PascalCaseStrEnum):
    TYPED_RESPONSE = auto()
    SELECT_ONE = auto()
    SELECT_ALL = auto()

class DataLabelingSelectOptions(TypedDict):
    text: Optional[str]

class DataLabelingSettings(TypedDict):
    prompt: Required[str]
    """(Required) The question text that will be presented to the participant (1-500 characters)."""

    dataLabelingResponseMethod: DataLabelingResponseMethod
    """The type of response the participant will give."""

    dataLabelingSelectOptions: list[DataLabelingSelectOptions]
    """Choice options that the participant can select from. Only valid for `SelectOne` and `SelectAll` `dataLabelingResponseMethod`."""

class TemplateSettings:
    htmlTemplateMarkup: Optional[str]
    """The html template markup. Should only be set if the template type is `CustomHtml`."""

    dataLabelingSettings: Optional[DataLabelingSettings]
    """Data Labeling Settings. Should only be set if the template type is `DataLabeling`."""

class TaskTemplate(TypedDict):
    taskTemplateType: Required[TaskTemplateType]
    """The type of task template."""

    headers: Required[list[str]]
    """(Non-Empty) The header columns for your data. All values need to be unique and match the numbers of cells in your data."""

    data: Required[list[TemplateDataRow]]
    """(Non-Empty) The data that should be distributed to participants."""

    settings: Required[TemplateSettings]
    """(Required) Template settings."""

class ProjectData(TypedDict, total=False):
    name: Required[str]
    """(Required) Name of your Connect project. This is visible to participants (500 characters max.)."""

    projectUrl: Optional[str]
    """The URL of your survey (e.g. Qualtrics)."""

    payment: Required[float]
    """(Required) The amount in USD that you will pay."""

    estimatedTimeInMinutes: Required[int]
    """(Required) How long in minutes you estimate a participant to complete your project. (2 minutes minimum)."""

    participants: Required[int]
    """(Required) The amount of participants (minimum 1 participant)."""

    summary: Optional[str]
    """Summary of your project (5000 characters max.)."""

    instructions: Optional[str]
    """
    Custom html instructions that are displayed to participants before beginning your project. 
    The max size limit for the instructions is 20MB.
    """

    internalName: Optional[str]
    """The internal name for your project. This will not be visible to participants."""

    systemRequirements: Optional[list[SystemRequirement]]
    """
    Additional requirements that your project needs in order for the participant to take your project.
    An empty array means that there are no additional requirements.
    """

    hasSensitiveContent: bool
    """Indicates that your project has content that can be considered sensitive content."""

    deviceRequirements: Optional[list[DeviceType]]
    """All the devices that the participant can use to take the project. An empty array allows all options."""

    completionSettings: CompletionSettings

    maxTimeInMinutes: Optional[int]
    """
    The maximum amount of minutes a participant will have to submit the project.
    Needs to be greater than `estimatedTimeInMinutes`. If this value is null then by default the maximum time will be
    set to a system optimized value based on your estimated time.
    """

    demographicTargeting: Optional[DemographicTargeting]
    """The demographic targeting criteria for your project."""

    platformTargeting: Optional[PlatformTargeting]
    """The platform targeting criteria for your project."""

    taskTemplate: Optional[TaskTemplate]
    "Template settings."

class ProjectResponseData(ProjectData):
    projectId: Optional[str]
    """The id of the Project."""

    totalCost: float
    """The total cost of the project including Connect fees."""

    createdAt: str
    """The UTC time the Project was created at."""

class ProjectResponse(TypedDict):
    project: Optional[ProjectResponseData]

class ProjectStatus(PascalCaseStrEnum):
    UNPUBLISHED = auto()
    PAUSED = auto()
    LIVE = auto()
    CLOSED = auto()
    COMPLETED = auto()
    ARCHIVED = auto()

class FilterQuery(TypedDict):
    Status: ProjectStatus
    """Filter to list projects that have are in a particular status."""

    Size: int
    """How many results to return. The default size is 10 and the max size is 100."""

    NextToken: str
    """A unique identifier that can be used to retrieve the next set of results. The token will expire after an hour."""

class ProjectResponsePage(TypedDict):
    projects: Optional[list[ProjectResponseData]]
    nextToken: Optional[str]

class ProjectStatistics(TypedDict):
    projectId: Optional[str]
    """The id of the Project."""

    pendingAssignments: int
    """The number of assignments that have not yet been approved or rejected."""

    completedAssignments: int
    """The number of assignments that have been approved or rejected."""

    inProgress: int
    """The number of participants currently taking your project."""

    approvedAssignments: int
    """The number of assignments that have been approved."""

    completionRate: float
    """Rate of total number of participants who started your project to how many actually completed it."""

    bounceRate: float
    """Rate of total number of participants who started your project to how many did not complete it."""

    averageDuration: float
    """Average time duration in minutes of completed assignments."""

    medianDuration: float
    """Median time duration in minutes of completed assignments."""

class Paginator:
    '''
    A paginator iterates through long lists of results. Each list is sliced into pages of
    items of a maximum length.
    
    Attributes:
        current_page: The most recent page of results that was retrieved. Is `None` if `next()` was
        not called on the paginator.
        session: The current Requests session. If `None`, then the most recent session created by `create_session()` is used.
        path: The endpoint path (not including the base url).
        query: An optional url query. It may be a query string or a `dict` of key value pairs.
        kwargs: Additional arguments to pass to the underlying `request()` function.
    '''
    def __init__(self, path: str, query: Optional[str | FilterQuery] = None, session: Optional[Session] = None, **kwargs):
        '''
        Args:
            session: The current Requests session. If `None`, then the most recent session created by `create_session()` is used.
            path: The endpoint path (not including the base url).
            query: An optional url query. It may be a query string or a `dict` of key value pairs.
            kwargs: Additional arguments to pass to the underlying `request()` function.
        '''
        self.path = path
        self.query = query
        self.session = session
        self.kwargs = kwargs
    
    def __iter__(self) -> Generator[None, ProjectResponseData, None]:
        match self.query:
            case dict():
                query = self.query.copy()
            case str():
                query = dict([(q.split('=', maxsplit=2)+[None])[:2] for q in query.split('&')])
            case None:
                query = None

        while True:
            current_page = base.get(self.path, query=query, session=self.session, **self.kwargs)

            for x in current_page.get('projects', []):
                yield x

            match query:
                case None | str():
                    query  = { 'NextToken': current_page.get('nextToken', None) }
                case _:
                    query['NextToken'] = current_page.get('nextToken', None)

            if query['NextToken'] is None:
                break

def create(project_data: ProjectData, session: Optional[Session]=None, idempotency_token: Optional[str]=None, **kwargs) -> ProjectResponse:
    """
    Create a project.
    
    
    The project will be created in a unpublished state and will need to be launched to start collecting data.
    
    Args:
        project_data: The parameters for creating a new project.
        session: The current Requests session. If `None`, use the last session that was created
        by `base.create_session()`.
        idempotency_token: A string used to identify this particular request to prevent duplicates.
        kwargs: Additional arguments to be passed to `session.request()`.

    Returns:
        The newly created project structure along with additional status information.
    
    Raises:
        ApiError:
            400 - Bad Request.
            401 - Invalid API or unauthorized resource access.
    """
    return base.post("/project", json=project_data, idempotency_token=idempotency_token, session=session, **kwargs)

def list_all(query: Optional[FilterQuery]=None, session: Optional[Session]=None, **kwargs) -> Paginator:
    """
    List projects.

    This can be used to list all projects for a particular account. The projects are
    ordered by their creation time in descending order, so newer projects will come first in the results.

    Args:
        query: A filter to limit list results.
        session: The current Requests session. If `None`, use the last session that was created
        by `base.create_session()`.
        kwargs: Additional arguments to be passed to `session.request()`.

    Returns:
        A page for a list of projects (including a `nextToken` to retrieve the next page in the sequence).
    
    Raises:
        ApiError:
            400 - Bad Request.
            401 - Invalid API or unauthorized resource access.
    """
    return Paginator("/project", query=query, session=session, **kwargs)

def retrieve(project_id: str, session: Optional[Session]=None, **kwargs) -> ProjectResponse:
    """
    Retrieve a project by ID.

    Args:
        project_id: The project ID.
        session: The current Requests session. If `None`, use the last session that was created
        by `base.create_session()`.
        kwargs: Additional arguments to be passed to `session.request()`.

    Returns:
        The project information.
    
    Raises:
        ApiError:
            400 - Bad Request.
            401 - Invalid API or unauthorized resource access.
    """
    return base.get(f"/project/{project_id}", session=session, **kwargs)

def edit(project_id: str, project_data: ProjectData, session: Optional[Session]=None, idempotency_token: Optional[str]=None, **kwargs) -> ProjectResponse:
    """
    Edit a project.

    An unpublished project can be fully edited. Once a project is published and is either in a `Live` or `Paused`
    state, you can only edit the following fields:

    * `name`
    * `projectUrl`
    * `participants` - You can only increase the spots available for participants.
    * `summary`
    * `instructions`

    Args:
        project_id: The project ID.
        project_data: The new data with which to update the project.
        session: The current Requests session. If `None`, use the last session that was created
        by `base.create_session()`.
        idempotency_token: A string used to identify this particular request to prevent duplicates.
        kwargs: Additional arguments to be passed to `session.request()`.

    Returns:
        The updated project.
    
    Raises:
        ApiError:
            400 - Bad Request.
            401 - Invalid API or unauthorized resource access.
    """
    return base.post(f"/project/{project_id}", json=project_data, idempotency_token=idempotency_token, session=session, **kwargs)

def update_status(project_id: str, status: ProjectStatus, session: Optional[Session]=None, idempotency_token: Optional[str]=None, **kwargs) -> None:
    """
    Update the status of your project.

    When a project's status is updated to `Live` participants will start taking your survey.
    There must be available funds in the account balance before transitioning a Project to `Live`,
    otherwise you will receive an insufficient funds error message.

    `Unpublished` - Can transition to `Live` and `Archived`.
    `Live` - Can only transition to `Paused`.
    `Paused` - Can only transition to `Live` or `Closed`.
    `Completed` - Project will be automatically set to `Completed` when all spots are filled.
    `Closed`
    `Archived`

    Args:
        project_id: The project ID.
        status: The new status of the Project.
        session: The current Requests session. If `None`, use the last session that was created
        by `base.create_session()`.
        idempotency_token: A string used to identify this particular request to prevent duplicates.
        kwargs: Additional arguments to be passed to `session.request()`.

    Raises:
        ApiError:
            400 - Bad Request.
            401 - Invalid API or unauthorized resource access.
    """
    base.post(f"/project/{project_id}/update-status",
                 json={ 'status': status },
                 json_response=False,
                 idempotency_token=idempotency_token,
                 session=session,
                 **kwargs)

def retrieve_statistics(project_id: str, session: Optional[Session]=None, **kwargs) -> ProjectStatistics:
    """
    Retrieve a project by ID.

    Args:
        project_id: The project ID.
        session: The current Requests session. If `None`, use the last session that was created
        by `base.create_session()`.
        kwargs: Additional arguments to be passed to `session.request()`.

    Returns:
        The project information.
    
    Raises:
        ApiError:
            400 - Bad Request.
            401 - Invalid API or unauthorized resource access.
    """
    return base.get(f"/project/{project_id}/statistics", session=session, **kwargs)
