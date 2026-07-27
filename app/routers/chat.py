import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User, Conversation, Message, MessageRole
from app.schemas import ChatRequest, ChatResponse
from app.services.agents import get_system_prompt
from app.services.memory import get_short_term_context, get_long_term_memory, build_context_block
from app.services.orchestrator import orchestrator
from app.services.skills import SKILL_DEFINITIONS, execute_skill
from app.limiter import limiter

logger = logging.getLogger("nexus.chat")

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# Contrato de saída que o frontend (Neural Core) sabe renderizar: resposta falável
# + painel contextual opcional. Isolado do prompt de persona de cada agente.
OUTPUT_FORMAT_INSTRUCTIONS = """
Você tem acesso a ferramentas (skills) reais — use-as sempre que ajudarem a responder com precisão
(hora atual, cálculo, clima, lembretes, tarefas, conversão de unidades) em vez de estimar de cabeça.
Depois de usar uma ferramenta, sua resposta final ainda deve seguir este formato:
Responda SEMPRE em JSON puro, sem markdown, sem crases, sem texto fora do JSON.
Formato exato:
{"reply": "resposta curta e falável, no máximo 2 frases", "panel": null | {"type": "list"|"info"|"metric", "title": "string curto", "items": ["string", "..."] | null, "value": "string" | null, "label": "string" | null}}
Use "panel" apenas quando a resposta ganhar clareza visual (listas, números, agenda). Para conversa simples, "panel": null.
O conteúdo de "reply" e de "panel" deve estar no MESMO idioma que o usuário usou na última mensagem.
Nunca inclua texto antes ou depois do JSON.
"""


def _parse_structured_reply(raw_text: str) -> dict:
    cleaned = raw_text.replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(cleaned)
        if "reply" in parsed:
            return {"reply": parsed.get("reply", ""), "panel": parsed.get("panel")}
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass
    logger.info("Resposta do modelo não veio em JSON estruturado, usando texto puro")
    return {"reply": raw_text, "panel": None}


def _build_messages(db: Session, conversation: Conversation, user_id: str) -> list:
    system_prompt = get_system_prompt(conversation.agent_type) + "\n\n" + OUTPUT_FORMAT_INSTRUCTIONS
    long_term = get_long_term_memory(db, user_id)
    context_block = build_context_block(long_term)
    full_system = system_prompt + ("\n\n" + context_block if context_block else "")
    history = get_short_term_context(db, conversation.id)
    return [{"role": "system", "content": full_system}] + history


def _get_owned_conversation(db: Session, conversation_id: str, user_id: str) -> Conversation:
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")
    if conversation.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem acesso a esta conversa")
    return conversation


@router.post("", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(
    request: Request,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = _get_owned_conversation(db, payload.conversation_id, current_user.id)

    user_msg = Message(conversation_id=conversation.id, role=MessageRole.user, content=payload.message)
    db.add(user_msg)
    db.commit()

    messages = _build_messages(db, conversation, current_user.id)

    async def skill_executor(tool_name: str, tool_input: dict) -> dict:
        return await execute_skill(tool_name, tool_input, db, current_user.id)

    try:
        result = await orchestrator.complete_with_tools(
            messages, tools=SKILL_DEFINITIONS, executor=skill_executor
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

    structured = _parse_structured_reply(result.text)

    assistant_msg = Message(
        conversation_id=conversation.id,
        role=MessageRole.assistant,
        content=structured["reply"],
        provider_used=result.provider_name,
    )
    db.add(assistant_msg)
    db.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        reply=structured["reply"],
        provider_used=result.provider_name,
        panel=structured["panel"],
        skills_used=result.tools_used,
    )


@router.post("/stream")
@limiter.limit("20/minute")
async def chat_stream(
    request: Request,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Streaming via Server-Sent Events. Use fetch() + ReadableStream no cliente
    (não EventSource — ele não manda o header Authorization).
    Eventos emitidos, um JSON por linha `data: `:
      {"type": "chunk", "text": "..."}         — pedaço de texto conforme chega
      {"type": "done", "provider_used": "..."} — fim do stream
      {"type": "error", "detail": "..."}       — falha (sem fallback pós-1º chunk)
    """
    conversation = _get_owned_conversation(db, payload.conversation_id, current_user.id)

    user_msg = Message(conversation_id=conversation.id, role=MessageRole.user, content=payload.message)
    db.add(user_msg)
    db.commit()

    messages = _build_messages(db, conversation, current_user.id)
    conversation_id = conversation.id
    user_id = current_user.id

    async def event_generator():
        accumulated = ""
        provider_used = None
        try:
            async for provider_name, chunk in orchestrator.stream_complete(messages):
                provider_used = provider_name
                accumulated += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'text': chunk}, ensure_ascii=False)}\n\n"
        except RuntimeError as exc:
            yield f"data: {json.dumps({'type': 'error', 'detail': str(exc)}, ensure_ascii=False)}\n\n"
            return

        # Persiste a resposta completa numa sessão de banco própria: a sessão
        # injetada por Depends(get_db) já pode ter sido fechada quando o
        # gerador termina de rodar (StreamingResponse encerra a request antes).
        # Resolve a fábrica de sessão pelo dependency_overrides atual do app
        # (em vez de importar SessionLocal direto) para respeitar overrides de
        # teste e qualquer configuração futura de múltiplos bancos.
        structured = _parse_structured_reply(accumulated)
        db_dependency = request.app.dependency_overrides.get(get_db, get_db)
        db_gen = db_dependency()
        stream_db = next(db_gen)
        try:
            stream_db.add(
                Message(
                    conversation_id=conversation_id,
                    role=MessageRole.assistant,
                    content=structured["reply"],
                    provider_used=provider_used,
                )
            )
            stream_db.commit()
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass

        yield f"data: {json.dumps({'type': 'done', 'provider_used': provider_used, 'panel': structured['panel']}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
