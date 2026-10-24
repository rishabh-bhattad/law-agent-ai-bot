import os
import uuid
import logging
from datetime import datetime, timezone
import httpx
from app.core.config import get_settings

logger = logging.getLogger(__name__)

def _get_api_key() -> str:
    """Retrieves the Revenium API key from settings, env, or revenium.env."""
    settings = get_settings()
    key = settings.REVENIUM_API_KEY or settings.REVENIUM_KEY or os.environ.get("REVENIUM_API_KEY") or os.environ.get("REVENIUM_KEY", "")
    if key:
        return key

    # Fallback: check ~/.gemini/revenium.env
    env_file = os.path.expanduser("~/.gemini/revenium.env")
    if os.path.isfile(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                content = f.read()
                # Check for revenium.api_key=rev_... or x-api-key=rev_...
                for part in content.replace("'", "").replace('"', '').split():
                    if "revenium.api_key=rev_" in part:
                        return part.split("revenium.api_key=")[1].split(",")[0]
                    if "x-api-key=rev_" in part:
                        return part.split("x-api-key=")[1].split(",")[0]
        except Exception:
            pass

    return ""


async def post_revenium_completion(
    model: str,
    provider: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    total_tokens: int = 0,
    reasoning_tokens: int = 0,
    cache_read_tokens: int = 0,
    cache_creation_tokens: int = 0,
    request_time: datetime | None = None,
    response_time: datetime | None = None,
    request_duration_ms: int = 0,
    task_type: str = "case-brief-generation",
    stop_reason: str = "END",
    is_streamed: bool = False,
) -> None:
    """Sends AI completion metering metadata to Revenium API."""
    api_key = _get_api_key()
    if not api_key:
        logger.debug("Revenium API key not configured; skipping metering.")
        return

    req_time = request_time or datetime.now(timezone.utc)
    res_time = response_time or datetime.now(timezone.utc)
    if request_duration_ms <= 0:
        request_duration_ms = max(1, int((res_time - req_time).total_seconds() * 1000))

    payload = {
        "stopReason": stop_reason,
        "costType": "AI",
        "isStreamed": is_streamed,
        "taskType": task_type,
        "agent": "legal-brief-agent",
        "operationType": "CHAT",
        "inputTokenCount": input_tokens,
        "outputTokenCount": output_tokens,
        "reasoningTokenCount": reasoning_tokens,
        "cacheCreationTokenCount": cache_creation_tokens,
        "cacheReadTokenCount": cache_read_tokens,
        "totalTokenCount": total_tokens or (input_tokens + output_tokens),
        "productName": "law-bot",
        "model": model,
        "transactionId": str(uuid.uuid4()),
        "responseTime": res_time.isoformat(),
        "requestDuration": request_duration_ms,
        "provider": provider,
        "requestTime": req_time.isoformat(),
        "completionStartTime": res_time.isoformat(),
        "timeToFirstToken": request_duration_ms,
    }

    endpoint = get_settings().REVENIUM_BASE_URL
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(endpoint, json=payload, headers=headers)
            if resp.status_code in (200, 201, 202):
                logger.info("Successfully metered %s (%s) to Revenium [%sms]", model, provider, request_duration_ms)
            else:
                logger.warning("Revenium metering responded with %s: %s", resp.status_code, resp.text)
    except Exception as e:
        logger.warning("Failed to dispatch telemetry to Revenium: %s", e)


def record_revenium_metric(
    model: str,
    provider: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    total_tokens: int = 0,
    reasoning_tokens: int = 0,
    cache_read_tokens: int = 0,
    cache_creation_tokens: int = 0,
    request_time: datetime | None = None,
    response_time: datetime | None = None,
    request_duration_ms: int = 0,
    task_type: str = "case-brief-generation",
) -> None:
    """Non-blocking fire-and-forget task to post metering to Revenium."""
    import asyncio
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(
            post_revenium_completion(
                model=model,
                provider=provider,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                reasoning_tokens=reasoning_tokens,
                cache_read_tokens=cache_read_tokens,
                cache_creation_tokens=cache_creation_tokens,
                request_time=request_time,
                response_time=response_time,
                request_duration_ms=request_duration_ms,
                task_type=task_type,
            )
        )
    except RuntimeError:
        # If no loop is running, skip gracefully
        pass
