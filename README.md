# pydantic-client

[![codecov](https://codecov.io/gh/ponytailer/pydantic-client/branch/main/graph/badge.svg?token=CZX5V1YP22)](https://codecov.io/gh/ponytailer/pydantic-client) [![Upload Python Package](https://github.com/ponytailer/pydantic-client/actions/workflows/python-publish.yml/badge.svg)](https://github.com/ponytailer/pydantic-client/actions/workflows/python-publish.yml)

Http client base pydantic with requests, aiohttp and httpx, support the json response or file(bytes).


#### If you like this project, please star it.

### How to install

> only support `requests`:
>> pip install pydantic-client

> support `aiohttp` and `requests`:
>> pip install "pydantic-client[aiohttp]"

> support `httpx(async)` and `requests`:
>> pip install "pydantic-client[httpx]"

> support all:
>> pip install "pydantic-client[all]"

### How to use

```python
from pydantic import BaseModel

from pydantic_client import delete, get, post, put, pydantic_client_manager
from pydantic_client import ClientConfig


class Book(BaseModel):
    name: str
    age: int


@pydantic_client_manager.register(
    ClientConfig(
        base_url="https://example.com",
        headers={"Authorization": "Bearer abcdefg"},
        timeout=10
    )
)
class WebClient:

    @get("/books/{book_id}?query={query}")
    def get_book(self, book_id: int, query: str) -> Book:
        ...

    @post("/books", form_body=True)
    def create_book_form(self, book: Book) -> Book:
        """ will post the form with book"""
        ...

    @put("/books/{book_id}")
    def change_book(self, book_id: int, book: Book) -> Book:
        """will put the json body"""
        ...

    @delete("/books/{book_id}")
    def change_book(self, book_id: int, request_headers: dict = None) -> Book:
        ...


client = pydantic_client_manager.get()
# will get the book with book_id=1
book: Book = client.get_book(1)

# request_headers will overwrite the headers in client_config
client.change_book(1, request_headers={"Authorization": "Bearer abcdefg"})

```

And see the examples.


<details>
<summary> Change Log </summary>

### v1.0.7: genearte client and schema code from swagger

```shell
pydantic-client parse your-swagger-file.yaml
```
you will get the code from output, above:

```python
from typing import Optional
from pydantic import BaseModel


class FunctionAnalysisRequest(BaseModel):
    project_name: str
    struct_code: str
    struct_level_code: str
    struct_name: Optional[str]
    function_type: str



class HTTPValidationError(BaseModel):
    detail: list[str]



class LoseEffectRequest(BaseModel):
    struct_name: Optional[str]
    function_description: Optional[str]



class LoseEffectResponse(BaseModel):
    failure_type_code: Optional[str]
    failure_description: Optional[str]


class WebClient:

    @get("/fmea-agent/v1/hello")
    def get_fmea_agent_v1_hello(self):
        ...

    @post("/fmea-agent/v1/function_analysis")
    def post_fmea_agent_v1_function_analysis(self, function_analysis_request: FunctionAnalysisRequest):
        ...

    @post("/fmea-agent/v1/lose_effect_analysis/{lose_id}")
    def post_fmea_agent_v1_lose_effect_analysis(self, lose_id: int, name: Optional[str], lose_effect_request: LoseEffectRequest):
        ...
```


### v1.0.5: support file response type.

```python
from pydantic_client.schema.file import File
from pydantic_client import post

@post("/download")
def download_file(self) -> File:
    # you will get the bytes content of the file
    ...

```

</details>
