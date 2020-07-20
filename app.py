"""
Simple app to test using WebHook storage with
a service where the details to retrieve the flow
are only known after building it.

In this case, the service generates an ID
and allows retrieving the flow by ID.
"""
import flask
import uuid

app = flask.Flask(__name__)

CACHE = {}


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/upload", methods=["POST"])
def upload_file():
    content = flask.request.get_data()
    flow_id = str(uuid.uuid4())
    CACHE[flow_id] = content
    return flask.jsonify(id=flow_id)


@app.route("/flows", methods=["GET"])
def list_files():
    return flask.jsonify(ids=list(CACHE.keys()))


@app.route("/flows/<flow_id>", methods=["GET"])
def fetch_flow(flow_id):
    return CACHE[flow_id]


app.run(host="0.0.0.0", port=8080)
