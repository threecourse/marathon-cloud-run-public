import os
import traceback

from flask import Flask, Response, json, request
from run import Runner

app = Flask(__name__)


@app.route("/")
def hello_world():
    # テスト用
    target = os.environ.get("TARGET", "World")
    return "Hello {}!\n".format(target)


@app.route("/run", methods=["POST"])
def run():
    # 常に成功のレスポンスを返すようにする
    try:
        # mime-application/json を入れなくても動くようにする
        req_payload = request.get_data().decode("utf-8")
        req_payload = json.loads(req_payload)
        results = Runner.run(req_payload)
        ret_payload = {}
        ret_payload["results"] = results
        ret_payload["status"] = "OK"
        ret_payload["exception"] = ""
        return Response(response=json.dumps(ret_payload), status=200)
    except Exception:
        ret_payload = {"status": "NG", "exception": f"{traceback.format_exc()}"}
        return Response(response=json.dumps(ret_payload), status=400)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
