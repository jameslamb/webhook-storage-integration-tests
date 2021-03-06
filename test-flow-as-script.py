"""
Test that storing a flow as a script works.
"""

import cloudpickle
import json
import os

from prefect.environments.storage import Webhook
from prefect import Flow

from sample_flow import flow

flow_script_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "sample_flow.py"
)
print(flow_script_path)


print(f"flow name: '{flow.name}'")


DBOX_APP_FOLDER = "/Apps/prefect-test-app"
flow.storage = Webhook(
    build_request_kwargs={
        "url": "https://content.dropboxapi.com/2/files/upload",
        "headers": {
            "Content-Type": "application/octet-stream",
            "Dropbox-API-Arg": json.dumps(
                {
                    "path": f"{DBOX_APP_FOLDER}/{flow.name}.py",
                    "mode": "overwrite",
                    "autorename": False,
                    "strict_conflict": True,
                }
            ),
            "Authorization": "Bearer ${DBOX_OAUTH2_TOKEN}"
        },
    },
    build_request_http_method="POST",
    get_flow_request_kwargs={
        "url": "https://content.dropboxapi.com/2/files/download",
        "headers": {
            "Accept": "application/octet-stream",
            "Dropbox-API-Arg": json.dumps({"path": f"{DBOX_APP_FOLDER}/{flow.name}.py"}),
            "Authorization": "Bearer ${DBOX_OAUTH2_TOKEN}"
        },
    },
    get_flow_request_http_method="POST",
    stored_as_script=True,
    flow_script_path=flow_script_path
)

flow.storage.add_flow(flow)

flow_file = "tmp.flow"

if os.path.isfile(flow_file):
    os.remove(flow_file)

with open(flow_file, "wb") as f:
    print(f"writing flow to '{flow_file}'")
    f.write(cloudpickle.dumps(flow))

if __name__ == "__main__":

    built_storage = flow.storage.build()
    assert isinstance(built_storage, Webhook)

    retrieved_flow = flow.storage.get_flow()
    assert isinstance(retrieved_flow, Flow)

    print("Done writing and reading flow")
