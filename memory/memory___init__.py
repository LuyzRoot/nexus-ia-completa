"""
Package entrypoint for memory subsystem.

Exports convenient functions used across the codebase:
- get_short_term_context
- get_long_term_memory
- upsert_memory
- build_context_block

Internally delegates to modules in this package.
"""
from .short_term import get_short_term_context, append_message, prune_conversation_if_needed
from .long_term import get_long_term_memory, upsert_memory, list_memory_keys, delete_memory
from .conversation import summarize_conversation, get_conversation_summary, set_conversation_summary
from .vector_store import VectorStore, get_default_vector_store
from .summarizer import summarize_messages, summarize_text

__all__ = [
    "get_short_term_context", "append_message", "prune_conversation_if_needed",
    "get_long_term_memory", "upsert_memory", "list_memory_keys", "delete_memory",
    "summarize_conversation", "get_conversation_summary", "set_conversation_summary",
    "VectorStore", "get_default_vector_store", "summarize_messages", "summarize_text",
]