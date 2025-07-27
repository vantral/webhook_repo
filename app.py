# deploy_hook.py

from flask import Flask, request, abort
import subprocess
import hmac
import hashlib
import os

app = Flask(__name__)

# Set this to your GitHub webhook secret
GITHUB_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "your-secret")
print(GITHUB_SECRET)

@app.route('/')
def hello():
    return "Hello from Flask + Gunicorn!"

@app.route("/deploy", methods=["POST"])
def github_webhook():
    print("deploying....")
    signature = request.headers.get("X-Hub-Signature-256")
    if signature is None:
        abort(403)

    sha_name, signature = signature.split('=')
    if sha_name != 'sha256':
        abort(501)

    mac = hmac.new(GITHUB_SECRET.encode(), msg=request.data, digestmod=hashlib.sha256)

    if not hmac.compare_digest(mac.hexdigest(), signature):
        abort(403)

    # Do the git pull
    subprocess.run(["git", "pull"])
    subprocess.run(["systemctl", "restart", "myapp"])
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=600)
