"""
This script is used to test creating `WebHook`
storage for use with a service for which
the get_flow() details can't be known until
after you upload the flow.

Run the app in this directory before this

    python app.py
"""
import cloudpickle
import json
import os
import random
import requests

from prefect import task, Task, Flow
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
    build_kwargs={
        "url": BUILD_ROUTE,
        "headers": {
            "Content-Type": "application/octet-stream",
        },
    },
    build_http_method="POST",
    get_flow_kwargs={
        "url": GET_ROUTE,
        "headers": {
            "Accept": "application/octet-stream",
        },
    },
    get_flow_http_method="GET",
)

flow.storage.add_flow(flow)

res = flow.storage.build()

# get the ID from the response
flow_id = res._build_responses[flow.name].json()["id"]

#  update storage
flow.storage.get_flow_kwargs["url"] = f"{GET_ROUTE}/{flow_id}"

fetched_flow = flow.storage.get_flow()

assert isinstance(fetched_flow, Flow)
assert fetched_flow.name == flow.name

# curl -X POST \
#     https://content.dropboxapi.com/2/files/upload \
#         -H "Authorization: Bearer ${DBOX_OAUTH2_TOKEN}" \
#         -H "Content-Type: application/octet-stream" \
#         --header "Dropbox-API-Arg: {\"path\": \"${DBOX_APP_FOLDER}/webhook.py\",\"mode\": \"add\",\"autorename\": true,\"mute\": false,\"strict_conflict\": false}" \
#         --data-binary @webhook.py

# curl -X POST https://content.dropboxapi.com/2/files/download \
#     --header "Authorization: Bearer " \
#     --header "Dropbox-API-Arg: {\"path\": \"/Homework/math/Prime_Numbers.txt\"}"

# # build()
# res = requests.post(
#     url="http://127.0.0.1:8080/upload",
#     headers={
#         "Content-Type": "application/octet-stream",
#     },
#     data=cloudpickle.dumps(flow),
# )

# flow_id = res.json()["id"]

# ids = requests.get(
#     url="http://127.0.0.1:8080/flows",
#     headers={
#         "Accept": "application/json",
#     },
# )

# res = requests.get(
#     url=f"http://127.0.0.1:8080/flows/{flow_id}",
#     headers={
#         "Accept": "application/octet-stream",
#     },
# )

# fetched_flow = cloudpickle.loads(res.content)
# assert isinstance(fetched_flow, Flow)
# assert fetched_flow.name == flow.name
