# memory_manager.py
from datetime import datetime
from langchain_core.messages import AIMessage
from memory.long_term_memory import vector_store, add_to_long_term
from memory.short_term_memory import get_redis_history
from dateparser import parse as parse_date


class MemoryManager:
    def __init__(self, session_id, user_id=None):
        self.session_id = session_id
        self.user_id = user_id
        self.history = get_redis_history(session_id)

    def fetch_context(self, query):
        """
        Check short-term memory first. If no relevant info found,
        fallback to long-term memory via vector search.
        """
        try:
            short_msgs = self.history.messages
            short_texts = [m.content for m in short_msgs if hasattr(m, "content")]

            # 1. Check if query is relevant to recent conversation
            if any(query.lower() in msg.lower() for msg in short_texts[-5:]):
                return short_msgs  # short-term is enough
        except Exception as e:
            print(f"Redis connection failed, using fallback: {e}")
            short_msgs = []
            short_texts = []

        # 2. Fallback: extract date if any, then vector search with metadata
        parsed_date = self.extract_date(query)
        metadata_filter = {"date": parsed_date} if parsed_date else None

        try:
            docs = vector_store.similarity_search(query, k=2, metadata=metadata_filter)
            retrieved = [AIMessage(content=doc.page_content) for doc in docs]
            return short_msgs + retrieved
        except Exception as e:
            print(f"Vector store failed, returning empty context: {e}")
            return short_msgs

    def extract_date(self, text):
        """
        Extract natural date (e.g., 'last Friday') and format to YYYY-MM-DD.
        """
        dt = parse_date(text, settings={"RELATIVE_BASE": datetime.now()})
        return dt.strftime("%Y-%m-%d") if dt else None

    def store_summary(self):
        """
        Extract full conversation and store it as long-term memory summary.
        Can be triggered periodically or after session ends.
        """
        try:
            all_msgs = self.history.messages
            full_text = "\n".join(m.content for m in all_msgs if hasattr(m, "content"))
            if len(full_text.strip()) > 100:  # basic cutoff for useful content
                metadata = {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "type": "summary",
                    "session_id": self.session_id
                }
                if self.user_id:  # Add user_id to metadata if available
                    metadata["user_id"] = self.user_id
                add_to_long_term(full_text, metadata=metadata)
        except Exception as e:
            print(f"Failed to store memory summary: {e}")
