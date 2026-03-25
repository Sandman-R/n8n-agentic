
from flask import Flask, request, jsonify
import subprocess
import json
import sys
from pathlib import Path

app = Flask(__name__)

def resolve_base_dir() -> Path:
    candidates = [
        Path(__file__).resolve().parents[1],
        Path.cwd(),
        Path.cwd().parent,
    ]
    for candidate in candidates:
        if (candidate / "testFiles" / "predict_product_sales.py").exists():
            return candidate
    return Path(__file__).resolve().parents[1]


BASE_DIR = resolve_base_dir()
SCRIPT_PATH = BASE_DIR / "testFiles" / "predict_product_sales.py"


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/predict/product", methods=["POST"])
def predict_product_sales():
    data = request.get_json(silent=True) or {}

    product_id = str(data.get("product_id", "")).strip()
    horizon = int(data.get("horizon", 12))
    params_path = str(data.get("params_path", "")).strip()

    if not product_id:
        return jsonify({"error": "product_id is required"}), 400
    if horizon <= 0:
        return jsonify({"error": "horizon must be > 0"}), 400
    if not SCRIPT_PATH.exists():
        return jsonify({"error": f"script not found: {SCRIPT_PATH}"}), 500

    cmd = [sys.executable, str(SCRIPT_PATH), product_id, str(horizon)]
    if params_path:
        cmd.append(params_path)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR),
        timeout=180,
    )

    if result.returncode != 0:
        return jsonify({
            "command": cmd,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }), 500

    stdout = result.stdout.strip()
    try:
        payload = json.loads(stdout) if stdout else {}
    except json.JSONDecodeError:
        return jsonify({
            "command": cmd,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "error": "script output is not valid JSON",
        }), 500

    return jsonify({
        "command": cmd,
        "returncode": result.returncode,
        "result": payload,
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)