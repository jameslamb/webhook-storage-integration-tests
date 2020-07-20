"""
Register a flow with Prefect Cloud. Assumes:

* flow is at `tmp.flow`
* run from a shell that has already authenticated with
    Prefect Cloud
* Prefect Cloud project is named "test-project"
"""

import cloudpickle

PROJECT_NAME = "test-project"

with open("tmp.flow", "rb") as f:
    flow = cloudpickle.loads(f.read())

flow.register(project_name=PROJECT_NAME, build=True)

print("done registering flow")
