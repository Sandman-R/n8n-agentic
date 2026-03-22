from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route("/run", methods=["POST"])
def run():
    data = request.get_json(silent=True) or {}
    filename = data.get("filename")

    if not filename:
        return jsonify({"error": "filename is required"}), 400

    result = subprocess.run(
        ["python", filename],
        capture_output=True,
        text=True
    )

    return jsonify({
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    })

app.run(host="0.0.0.0", port=8000)