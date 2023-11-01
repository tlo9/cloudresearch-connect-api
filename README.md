# Unofficial Python Bindings for CloudResearch Connect API

Requirements: >= Python 3.10

## API Key

In order to make API calls, you will need an API key. Contact [CloudResearch support](mailto:support@cloudresearch.com)
to create an API key.

Once you have a key, call `create_session()` with your key, or set the `X-API-KEY` header for a `requests.Session`
object and use it with each API call.

## Idempotency Tokens

Some API calls, such as for creating projects or paying bonuses, accept an optional idempotency token that is used
to prevent duplicate requests. Attempting to send two or more requests with the same token will fail, even if the
request resulted in a failure. Idempotency tokens expire after 24 hours.

## Functions

Note: Async functions are not (yet) supported.

### base

```
create_session(api_key: str) -> Session:
```

### account

```
get_info() -> AccountInfo
```

### assignments

```
list_all(project_id: str) -> AssignmentResponse
approve(project_id: str, participants: list[Participant])
approve_all(project_id: str, message: Optional[str])
reject(project_id: str, participants: list[Participant])
bonus(project_id: str, bonus_payments: list[BonusPayment])
reverse_rejections(project_id: str, participants: list[Participant])
```

### demographics

```
list_all() -> DemographicsResponse
calc_feasibility(data: FeasibilityRequest) -> FeasibilityResponse
```

### project

```

create(project_data: ProjectData) -> ProjectResponse
list_all(query: Optional[FilterQuery] = None) -> ProjectResponsePage
retrieve(project_id: str) -> ProjectResponse
edit(project_id: str, project_data: ProjectData) -> ProjectResponse
update_status(project_id: str, status: ProjectStatus)
retrieve_statistics(project_id: str) -> ProjectStatistics
```

## Usage

```
from tism.cr_connect import base, account

if __name__ == '__main__':
    api_key = 'YOUR-API-KEY'

    base.create_session(api_key)
    acct_info: account.AccountInfo = account.get_info()

    print(f'Account balance: {acct_info.accountBalance}')
```

CloudResearch is a registered trademark of Prime Research Solutions LLC
