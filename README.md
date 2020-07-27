# webhook-storage-integration-tests

This is a temporary repo with integration tests for INSERT PR LINK.

#### Contents

1. [Installation](#installation)
1. [Example 1: DropBox](#dropbox)
    * [local](#dropbox-local)
    * [Prefect Cloud](#dropbox-cloud)
1. [Example 2: When `get_flow()` depends on `build()`](#get-flow)
    * [local](#get-flow-local)
    * [Prefect Cloud](#get-flow-cloud)
1. [Example 3: flow stored as script](#script)
    * [local](#get-flow-local)
    * [Prefect Cloud](#get-flow-cloud)

## Installation

To install `prefect` from that PR:

```shell
pip install git+https://github.com/jameslamb/prefect@feat/webhook-storage
```

## DropBox <a name="dropbox"></a>

This section describes how to test that `WebHook` storage can be used to store flows with DropBox.

### Local <a name="dropbox-local"></a>

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


### Testing with Prefect Cloud <a name="dropbox-cloud"></a>

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
python register-flow.py
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
prefect run cloud \
    --name test-flow \
    --project test-project
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


## When `get_flow()` depends on `build()` <a name="get-flow"></a>

This section can be used to test that `WebHook` storage is able to accomodate the case where `get_flow()` needs some details that can only be determined by running `build()`.

In this example, I've written a small service with the following endpoints:

* `POST /upload`: given the content of a flow, assign it a unique id and store it under that id
* `GET /flows/{flow_id}`: get the content of a flow by id

In this case, `build()` needs to run `POST /upload`, then update the details of the flow with the `flow_id` that is returned.

### Local <a name="get-flow-local"></a>

1. Run the service locally. It will serve on `127.0.0.0:8080`

```shell
python app.py
```

2. In another terminal, test storing and retrieving the flow.

```shell
python test-build-details.py
```

You should see something like this in the app's logs

```text
 * Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)
127.0.0.1 - - [20/Jul/2020 00:52:10] "POST /upload HTTP/1.1" 200 -
127.0.0.1 - - [20/Jul/2020 00:52:10] "GET /flows/d4d93341-f94b-4f49-a6ac-9ecbc263f4d9 HTTP/1.1" 200 -
```

And something like this in the Python script's logs:

```text
Result check: OK
[2020-07-20 05:52:10] INFO - prefect.WebHook | Uploading flow 'test-flow'
[2020-07-20 05:52:10] INFO - prefect.WebHook | Successfully uploaded flow 'test-flow'
[2020-07-20 05:52:10] INFO - prefect.WebHook | Retrieving flow
```

### Prefect Cloud <a name="get-flow-cloud"></a>

Repeat the setup steps for Prefect Cloud [from the DropBox example](#dropbox-cloud), abbreviated here.

In one shell:

```shell
prefect agent start \
    --token ${PREFECT_RUNNER_TOKEN} \
    --label webhook-flow-storage
```

In another shell:

```shell
python test-build-details.py
prefect auth login -t ${PREFECT_USER_TOKEN}
python register-flow.py

prefect run cloud \
    --name test-flow \
    --project test-project
```

After a few seconds, you should see evidence that this is working correctly.

**agent**

The `LocalAgent` should have been asked to run the flow

```text
[2020-07-20 06:05:46,246] INFO - agent | Found 1 flow run(s) to submit for execution.
[2020-07-20 06:05:46,390] INFO - agent | Deploying flow run 1ebb481c-7aff-45a5-9103-e05c419b8a08
```

**app logs**

The little Flask app should have gotten a new request for the flow

```text
127.0.0.1 - - [20/Jul/2020 01:05:47] "GET /flows/1f08f4bc-f427-459e-94a3-9e5f756062ec HTTP/1.1" 200 -
```

**Prefect Cloud**

You should see a new, successful flow run in the Prefect Cloud UI. The logs for that run should end with something like this.

```text
20 July 2020,01:05:48   prefect.CloudFlowRunner INFO    Flow run SUCCESS: all reference tasks succeeded
20 July 2020,01:05:48   prefect.CloudFlowRunner DEBUG   Flow 'test-flow': Handling state change from Running to Success
```

## Flow stored as script <a name="script"></a>

This section describes how to test that `Webhook` storage works for a flow stored as a script (`stored_as_script=True`).

### Local <a name="script-local"></a>

Follow all the steps from [DropBox local](#dropbox-local), but run this script instead of `test-dropbox.py`:

```shell
python test-dropbox.py
```

### Prefect Cloud <a name="script-cloud"></a>

Repeat all the steps from [the DropBox section on Prefect Cloud](#dropbox-cloud).
