"""
This script is used to test creating `WebHook`
storage for use with a service for which
the get_flow() details can't be known until
after you upload the flow.

Run the app in this directory before this

    python app.py
"""
import cloudpickle
import os
import random

from prefect import task, Flow
from prefect.environments.storage import WebHook

BASE_URL = "http://127.0.0.1:8080"
BUILD_ROUTE = f"{BASE_URL}/upload"
GET_ROUTE = f"{BASE_URL}/flows"


@task
def random_number():
    return random.randint(0, 100)


with Flow("test-flow") as flow:
    random_number()


flow.storage = WebHook(
    build_kwargs={"url": BUILD_ROUTE, "headers": {"Content-Type": "application/octet-stream"}},
    build_http_method="POST",
    get_flow_kwargs={"url": GET_ROUTE, "headers": {"Accept": "application/octet-stream"}},
    get_flow_http_method="GET",
)

flow.storage.add_flow(flow)

res = flow.storage.build()

# get the ID from the response
flow_id = res._build_responses[flow.name].json()["id"]

#  update storage
flow.storage.get_flow_kwargs["url"] = f"{GET_ROUTE}/{flow_id}"

# write the flow to disk after patching it, to test with Cloud
flow_file = "tmp.flow"

if os.path.isfile(flow_file):
    os.remove(flow_file)

with open(flow_file, "wb") as f:
    print(f"writing flow to '{flow_file}'")
    f.write(cloudpickle.dumps(flow))

fetched_flow = flow.storage.get_flow()

assert isinstance(fetched_flow, Flow)
assert fetched_flow.name == flow.name
