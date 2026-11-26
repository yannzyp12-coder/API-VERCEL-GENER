"""
FF Guest Account Generator API
Entry point untuk Vercel serverless (Flask)

Endpoints:
  POST /generate            — buat N akun guest
  GET  /accounts            — list akun dari Firebase
  GET  /accounts/<id>       — get satu akun
  DELETE /accounts/<id>     — hapus akun
  GET  /health              — health check
  GET  /                    — info
"""
import os
import sys
import time

# Path fix untuk Vercel — pastikan root project ke sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from flask import Flask, request, jsonify
from core.generator import generate_guest_account
from db.firebase    import save_account, get_account, list_accounts, delete_account

app = Flask(__name__)

RELEASE_VER = os.environ.get("RELEASE_VERSION", "OB55")


# ── Helper ──────────────────────────────────────────────────────────

def _strip_internal(account: dict) -> dict:
    """Hapus key internal (_elapsed_sec, dll) dari response."""
    return {k: v for k, v in account.items() if not k.startswith("_")}


def _parse_args() -> dict:
    if request.method == "GET":
        return dict(request.args)
    ct = request.content_type or ""
    if "json" in ct:
        return request.get_json(silent=True) or {}
    return dict(request.form) or {}


# ── Routes ──────────────────────────────────────────────────────────

@app.route("/generate", methods=["GET", "POST"])
def route_generate():
    """
    Buat N akun guest FF.
    Params:
      count  int   default 1, max 10
      region str   default ID
      save   bool  default true  → simpan ke Firebase
    Response format:
    {
      "accounts":        [...],
      "cache_fresh":     N,
      "cache_hit":       false,
      "cache_used":      0,
      "elapsed_sec":     0.74,
      "ghost":           false,
      "region":          "ID",
      "release_version": "OB55",
      "success":         true,
      "total_created":   N,
      "total_requested": N
    }
    """
    t0   = time.perf_counter()
    args = _parse_args()

    count       = min(int(args.get("count", 1)), 10)
    region      = str(args.get("region", "ID")).upper()
    do_save     = str(args.get("save", "true")).lower() != "false"
    name_prefix = str(args.get("name_prefix", ""))

    accounts    = []
    errors      = []
    cache_fresh = 0

    for i in range(count):
        try:
            acc = generate_guest_account(region=region, name_prefix=name_prefix)
            if do_save:
                try:
                    save_account(acc)
                    cache_fresh += 1
                except Exception as fe:
                    acc["_firebase_error"] = str(fe)
            accounts.append(_strip_internal(acc))
        except Exception as e:
            errors.append({"index": i, "error": str(e)})
        time.sleep(0.05)

    elapsed = round(time.perf_counter() - t0, 2)
    success = len(accounts) > 0

    body = {
        "accounts":        accounts,
        "cache_fresh":     cache_fresh,
        "cache_hit":       False,
        "cache_used":      0,
        "elapsed_sec":     elapsed,
        "ghost":           any(a.get("is_ghost") for a in accounts),
        "region":          region,
        "release_version": RELEASE_VER,
        "success":         success,
        "total_created":   len(accounts),
        "total_requested": count,
    }
    if errors:
        body["errors"] = errors

    return jsonify(body), (200 if success else 500)


@app.route("/accounts", methods=["GET"])
def route_list():
    """
    List akun dari Firebase.
    Params: region (optional), limit (default 50)
    """
    region = request.args.get("region")
    limit  = int(request.args.get("limit", 50))
    try:
        accs = list_accounts(region=region, limit=limit)
        return jsonify({"accounts": accs, "total": len(accs), "success": True})
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/accounts/<account_id>", methods=["GET"])
def route_get(account_id: str):
    """Get satu akun by account_id."""
    try:
        acc = get_account(account_id)
        if not acc:
            return jsonify({"error": "not found"}), 404
        return jsonify(acc)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/accounts/<account_id>", methods=["DELETE"])
def route_delete(account_id: str):
    """Hapus akun dari Firebase."""
    try:
        delete_account(account_id)
        return jsonify({"deleted": account_id, "success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status":          "ok",
        "release_version": RELEASE_VER,
    })


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "api":     "API VERCEL GEN GUEST — DBECKKZ",
        "version": "2.0.0",
        "endpoints": {
            "POST /generate":          "Buat akun guest. Params: count, region, save, name_prefix",
            "GET  /accounts":          "List akun Firebase. Params: region, limit",
            "GET  /accounts/:id":      "Get akun by ID",
            "DELETE /accounts/:id":    "Hapus akun",
            "GET  /health":            "Health check",
        },
        "example_request": {
            "url":    "/generate",
            "method": "POST",
            "body":   {"count": 1, "region": "ID", "save": True},
        },
    })


# Local dev
if __name__ == "__main__":
    app.run(debug=True, port=5000)
