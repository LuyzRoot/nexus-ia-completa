from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import asyncio
import logging
from fastapi.responses import StreamingResponse

from inference.predictor import Predictor
from inference.sse import sse_event_generator

logger = logging.getLogger("inference.routes")
router = APIRouter()

# Request/Response models
class MessageItem(BaseModel):
    role: str
    content: str

class InferenceRequest(BaseModel):
    messages: List[MessageItem]
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stop: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class InferenceResponse(BaseModel):
    text: str
    provider: Optional[str] = None
    model: Optional[str] = None
    tools_used: Optional[List[str]] = None

class StreamRequest(BaseModel):
    messages: List[MessageItem]
    temperature: Optional[float] = 0.2

class RetrieveRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    rerank: Optional[bool] = True

class BatchRequest(BaseModel):
    requests: List[InferenceRequest]

_predictor = Predictor()

@router.post("", response_model=InferenceResponse)
async def inference(payload: InferenceRequest):
    try:
        messages = [m.dict() for m in payload.messages]
        resp = await _predictor.generate(messages, temperature=payload.temperature, max_tokens=payload.max_tokens)
        return {"text": resp.text, "provider": resp.provider_name, "model": resp.model, "tools_used": resp.tools_used}
    except Exception as exc:
        logger.exception("Inference failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/stream")
async def inference_stream(payload: StreamRequest):
    """
    Streamed inference using SSE. Each SSE event is JSON with {'chunk': 'text part'}.
    """
    async def event_stream():
        try:
            messages = [m.dict() for m in payload.messages]
            async for chunk in _predictor.stream_generate(messages, temperature=payload.temperature):
                yield f"data: {chunk}\n\n"
        except Exception as exc:
            logger.exception("Streaming failed: %s", exc)
            yield f"event: error\ndata: {str(exc)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/retrieve")
async def retrieve_and_generate(payload: RetrieveRequest):
    """
    Retrieval augmented generation: retrieve passages and then call LLM with context.
    Returns: {"query":..., "retrieved":[{id,score,metadata,text}], "answer": {...}}
    """
    try:
        retrieved, answer = await _predictor.generate_with_retrieval(payload.query, top_k=payload.top_k, rerank=payload.rerank)
        return {"query": payload.query, "retrieved": retrieved, "answer": {"text": answer.text, "provider": answer.provider_name, "model": answer.model}}
    except Exception as exc:
        logger.exception("RAG inference failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/batch")
async def batch_inference(payload: BatchRequest):
    """
    Simple batch endpoint: processes requests sequentially.
    For large scale use a proper batcher/worker or GPU batching backend.
    """
    out = []
    for req in payload.requests:
        messages = [m.dict() for m in req.messages]
        try:
            r = await _predictor.generate(messages, temperature=req.temperature, max_tokens=req.max_tokens)
            out.append({"text": r.text, "provider": r.provider_name, "model": r.model})
        except Exception as exc:
            logger.exception("Batch item failed: %s", exc)
            out.append({"error": str(exc)})
    return {"results": out}