from fastapi import APIRouter, Request, HTTPException
from backend.commands.holders_avg_entry_price import get_holders_avg_entry_price
from backend.commands.top_holders_holdings import get_top_holders_holdings
from backend.commands.fresh_wallets import fresh_wallets
from backend.commands.fresh_wallets_v2 import fresh_wallets_v2
from backend.commands.noteworthy_addresses import get_noteworthy_addresses
from backend.commands.holding_distribution import get_holding_distribution

from datetime import datetime
import json
import os

router = APIRouter()
LOG_FILE = "backend/api/logs.json"


def save_request_log(endpoint: str, ip: str, user_agent: str, token: str, limit: int, success: bool, error: str = None):
    """Save request metadata to logs.json, including success and error (if any)."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "endpoint": endpoint,
        "ip": ip,
        "user_agent": user_agent,
        "token": token,
        "limit": limit,
        "success": success,
    }

    if error:
        log_entry["error"] = error

    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    data.append(log_entry)

    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)


async def fetch_data(func, token: str, limit: int):
    """Helper function to handle async API calls."""
    return await func(token=token, limit=limit)


@router.get("/avg_entry/")
async def avg_entry(token: str, request: Request, limit: int = 50):
    if not token:
        raise HTTPException(status_code=400, detail="Token address is required")

    limit = min(limit, 50)
    ip = request.client.host
    ua = request.headers.get("user-agent")

    try:
        result = await fetch_data(get_holders_avg_entry_price, token, limit)
        save_request_log("/avg_entry/", ip, ua, token, limit, success=True)
        return {"success": True, "data": result}
    except Exception as e:
        save_request_log("/avg_entry/", ip, ua, token, limit, success=False, error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/top-holders/")
async def top_holders(token: str, request: Request, limit: int = 50):
    if not token:
        raise HTTPException(status_code=400, detail="Token address is required")

    limit = min(limit, 50)
    ip = request.client.host
    ua = request.headers.get("user-agent")

    try:
        result = await fetch_data(get_top_holders_holdings, token, limit)
        save_request_log("/top-holders/", ip, ua, token, limit, success=True)
        return {"success": True, "data": result}
    except Exception as e:
        save_request_log("/top-holders/", ip, ua, token, limit, success=False, error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/fresh_holders/")
async def fresh_holders(token: str, request: Request, limit: int = 50):
    if not token:
        raise HTTPException(status_code=400, detail="Token address is required")

    limit = min(limit, 50)
    ip = request.client.host
    ua = request.headers.get("user-agent")

    try:
        result = await fetch_data(fresh_wallets, token, limit)
        save_request_log("/fresh_holders/", ip, ua, token, limit, success=True)
        return {"success": True, "data": result}
    except Exception as e:
        save_request_log("/fresh_holders/", ip, ua, token, limit, success=False, error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
