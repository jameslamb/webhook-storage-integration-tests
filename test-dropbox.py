import cloudpickle
import json
import os
import random

import prefect
from prefect import task, Flow
from prefect.environments.storage import WebHook

FLOW_NAME = "test-flow"
print(f"flow name: '{FLOW_NAME}'")


@task
def random_number():
    logger = prefect.context.get("logger")
    num = random.randint(0, 100)
    logger.info(f"random number: {num}")
    return num


with Flow(FLOW_NAME) as flow:
    r = random_number()


DBOX_APP_FOLDER = "/Apps/prefect-test-app"
flow.storage = WebHook(
    build_kwargs={
        "url": "https://content.dropboxapi.com/2/files/upload",
        "headers": {
            "Content-Type": "application/octet-stream",
            "Dropbox-API-Arg": json.dumps(
                {
                    "path": f"{DBOX_APP_FOLDER}/{flow.name}.flow",
                    "mode": "overwrite",
                    "autorename": False,
                    "strict_conflict": True,
                }
            ),
        },
    },
    build_http_method="POST",
    get_flow_kwargs={
        "url": "https://content.dropboxapi.com/2/files/download",
        "headers": {
            "Content-Type": "application/octet-stream",
            "Dropbox-API-Arg": json.dumps({"path": f"{DBOX_APP_FOLDER}/{flow.name}.flow"}),
        },
    },
    get_flow_http_method="POST",
    build_secret_config={"Authorization": {"name": "DBOX_OAUTH2_TOKEN", "type": "environment"}},
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
    assert isinstance(built_storage, WebHook)

    retrieved_flow = flow.storage.get_flow()
    assert isinstance(retrieved_flow, Flow)

    print("Done writing and reading flow")
