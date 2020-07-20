# webhook-storage-integration-tests

This is a temporary repo with integration tests for INSERT PR LINK.

## DropBox

This section describes how to test that `WebHook` storage can be used to store flows with DropBox.

**Roundtripping**

1. go to https://www.dropbox.com/developers/apps/create
2. choose "DropBox API"
3. chooose "App folder"
    - name your app "prefect-test-app"
    - all files will end up in a folder with the same name as the app
    - in this case, "/Apps/prefect-test-app"
4. generate an Oauth2 access token and save it somewhere
5. Put that oauth2 token in an environment variable, prefixed with "Bearer "

```shell
DBOX_TOKEN="your token here"
export DBOX_OAUTH2_TOKEN="Bearer ${DBOX_TOKEN}"
```

6. Run the test script

```shell
python test-dropbox.py
```

> [2020-07-20 04:10:32] INFO - prefect.WebHook | Uploading flow 'test-flow'

7. Log in to dropbox.com. Confirm that you see a file `/Apps/prefect-test-app/{that_id}.flow`.


## Testing with Prefect Cloud

To test with Prefect Cloud, get a Prefect `USER` token, and log in.

```shell
prefect auth login -t ${PREFECT_USER_TOKEN}
```

Create a project

```shell
PROJECT_NAME="test-project"
prefect create project ${PROJECT_NAME}
```

Register the flow

```python
import cloudpickle

with open("tmp.flow", "rb") as f:
    flow = cloudpickle.loads(f.read())

flow.register(
    project_name="test-project",
    build=True
)
```

You should see logs like this:

> [2020-07-20 04:23:33] INFO - prefect.WebHook | Uploading flow 'test-flow'

>  [2020-07-20 04:23:34] INFO - prefect.WebHook | Successfully uploaded flow 'test-flow'

Go to Prefect Cloud and get a `RUNNER` token

```shell
prefect agent start \
    --token ${PREFECT_RUNNER_TOKEN} \
    --label webhook-flow-storage
```

In a separate shell, run the following:

```shell
prefect run cloud --name test-flow --project test-project
```

You should see logs like this in the agent

```text
 ____            __           _        _                    _
|  _ \ _ __ ___ / _| ___  ___| |_     / \   __ _  ___ _ __ | |_
| |_) | '__/ _ \ |_ / _ \/ __| __|   / _ \ / _` |/ _ \ '_ \| __|
|  __/| | |  __/  _|  __/ (__| |_   / ___ \ (_| |  __/ | | | |_
|_|   |_|  \___|_|  \___|\___|\__| /_/   \_\__, |\___|_| |_|\__|
                                           |___/

[2020-07-20 04:34:45,397] INFO - agent | Starting LocalAgent with labels ['webhook-flow-storage', 'Jamess-MBP', 'azure-flow-storage', 'gcs-flow-storage', 's3-flow-storage', 'github-flow-storage', 'webhook-flow-storage']
[2020-07-20 04:34:45,398] INFO - agent | Agent documentation can be found at https://docs.prefect.io/orchestration/
[2020-07-20 04:34:45,398] INFO - agent | Agent connecting to the Prefect API at https://api.prefect.io
[2020-07-20 04:34:45,468] INFO - agent | Waiting for flow runs...
[2020-07-20 04:35:01,819] INFO - agent | Found 1 flow run(s) to submit for execution.
[2020-07-20 04:35:01,957] INFO - agent | Deploying flow run c12d96cd-0368-49b1-bebc-6474b0f0fbe0
```

In the Prefect Cloud UI, look at the logs for this flow's run. They should end like this:

```text
19 July 2020,11:35:04   prefect.CloudFlowRunner INFO    Flow run SUCCESS: all reference tasks succeeded
19 July 2020,11:35:04   prefect.CloudFlowRunner DEBUG   Flow 'test-flow': Handling state change from Running to Success
```

**References**

* https://www.dropbox.com/developers/documentation/http/documentation#auth-token-from_oauth1
* https://www.dropbox.com/developers/reference/auth-types#app