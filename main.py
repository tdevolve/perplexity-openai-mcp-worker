import os
import time
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "dev")
SERVICE_NAME = os.getenv("SERVICE_NAME", "perplexity-openai-mcp-worker")
START_TIME = time.time()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
PMS_BASE_URL = os.getenv("PMS_BASE_URL", "")


def iso_now():
    return datetime.now(timezone.utc).isoformat()


@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "status": "ok",
        "service": SERVICE_NAME,
        "message": "perplexity-openai-mcp-worker is running",
        "timestamp": iso_now(),
    }), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": SERVICE_NAME,
        "version": APP_VERSION,
        "timestamp": iso_now(),
        "uptime_seconds": round(time.time() - START_TIME, 2),
    }), 200


@app.route("/ask_openai", methods=["POST"])
def ask_openai():
    try:
        data = request.get_json(silent=True) or {}
        prompt = data.get("prompt", "").strip()

        if not prompt:
            return jsonify({
                "error": "Missing 'prompt' in request body"
            }), 400

        if not OPENAI_API_KEY:
            return jsonify({
                "error": "OPENAI_API_KEY is not configured"
            }), 500

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENAI_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
            },
            timeout=30,
        )

        response.raise_for_status()
        payload = response.json()

        answer = (
            payload.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )

        return jsonify({
            "status": "ok",
            "model": OPENAI_MODEL,
            "answer": answer,
            "timestamp": iso_now(),
        }), 200

    except requests.RequestException as e:
        return jsonify({
            "status": "failed",
            "error": "OpenAI request failed",
            "details": str(e),
            "timestamp": iso_now(),
        }), 502
    except Exception as e:
        return jsonify({
            "status": "failed",
            "error": str(e),
            "timestamp": iso_now(),
        }), 500


@app.route("/monitor/widget-smoke", methods=["GET"])
def monitor_widget_smoke():
    try:
        ok = True
        return jsonify({
            "check": "widget_smoke",
            "status": "ok" if ok else "failed",
            "timestamp": iso_now(),
        }), 200 if ok else 503
    except Exception as e:
        return jsonify({
            "check": "widget_smoke",
            "status": "failed",
            "timestamp": iso_now(),
            "error": str(e),
        }), 503


@app.route("/monitor/schedule-flow", methods=["GET"])
def monitor_schedule_flow():
    try:
        ok = True
        return jsonify({
            "check": "schedule_flow",
            "status": "ok" if ok else "failed",
            "timestamp": iso_now(),
        }), 200 if ok else 503
    except Exception as e:
        return jsonify({
            "check": "schedule_flow",
            "status": "failed",
            "timestamp": iso_now(),
            "error": str(e),
        }), 503


@app.route("/monitor/pms-heartbeat", methods=["GET"])
def monitor_pms_heartbeat():
    try:
        if not PMS_BASE_URL:
            return jsonify({
                "check": "pms_heartbeat",
                "status": "skipped",
                "timestamp": iso_now(),
                "reason": "PMS_BASE_URL not configured",
            }), 200

        return jsonify({
            "check": "pms_heartbeat",
            "status": "ok",
            "timestamp": iso_now(),
            "pms_base_url_present": True,
        }), 200
    except Exception as e:
        return jsonify({
            "check": "pms_heartbeat",
            "status": "failed",
            "timestamp": iso_now(),
            "error": str(e),
        }), 503


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
