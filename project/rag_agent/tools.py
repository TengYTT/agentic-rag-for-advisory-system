from typing import List
from langchain_core.tools import tool
from db.parent_store_manager import ParentStoreManager


def _format_chunk_with_tier(doc):
    """Format a retrieved chunk with tier metadata for LLM consumption.
    Handles both LangChain Document objects and plain dicts (from parent store).
    Falls back gracefully when tier fields are missing.
    """
    is_document = hasattr(doc, 'metadata')
    meta = doc.metadata if is_document else doc.get('metadata', {})

    if is_document:
        parent_id = meta.get('parent_id', '')
        content = doc.page_content
    else:
        parent_id = doc.get('parent_id', meta.get('parent_id', ''))
        content = doc.get('content', '')

    parts = [
        f"Parent ID: {parent_id}",
        f"File Name: {meta.get('source', '')}",
    ]

    tier = meta.get('source_tier')
    source_type = meta.get('source_type', 'unknown')
    parts.append(f"Source Tier: {tier} ({source_type})" if tier is not None else "Source Tier: unknown")

    primary_url = meta.get('primary_url')
    if primary_url:
        parts.append(f"Primary URL: {primary_url}")

    last_retrieved = meta.get('last_retrieved')
    if last_retrieved:
        parts.append(f"Last Retrieved: {last_retrieved}")

    parts.append(f"Content: {content.strip()}")
    return "\n".join(parts)


class ToolFactory:

    def __init__(self, collection):
        self.collection = collection
        self.parent_store_manager = ParentStoreManager()

    def _search_child_chunks(self, query: str, limit: int) -> str:
        """Search for the top K most relevant child chunks.

        Args:
            query: Search query string
            limit: Maximum number of results to return
        """
        try:
            results = self.collection.similarity_search(query, k=limit, score_threshold=0.7)
            if not results:
                return "NO_RELEVANT_CHUNKS"

            return "\n\n".join([_format_chunk_with_tier(doc) for doc in results])

        except Exception as e:
            return f"RETRIEVAL_ERROR: {str(e)}"

    def _retrieve_many_parent_chunks(self, parent_ids: List[str]) -> str:
        """Retrieve full parent chunks by their IDs.

        Args:
            parent_ids: List of parent chunk IDs to retrieve
        """
        try:
            ids = [parent_ids] if isinstance(parent_ids, str) else list(parent_ids)
            raw_parents = self.parent_store_manager.load_content_many(ids)
            if not raw_parents:
                return "NO_PARENT_DOCUMENTS"

            return "\n\n".join([_format_chunk_with_tier(doc) for doc in raw_parents])

        except Exception as e:
            return f"PARENT_RETRIEVAL_ERROR: {str(e)}"

    def _retrieve_parent_chunks(self, parent_id: str) -> str:
        """Retrieve full parent chunks by their IDs.

        Args:
            parent_id: Parent chunk ID to retrieve
        """
        try:
            parent = self.parent_store_manager.load_content(parent_id)
            if not parent:
                return "NO_PARENT_DOCUMENT"

            return _format_chunk_with_tier(parent)

        except Exception as e:
            return f"PARENT_RETRIEVAL_ERROR: {str(e)}"

    def create_tools(self) -> List:
        """Create and return the list of tools."""
        search_tool = tool("search_child_chunks")(self._search_child_chunks)
        retrieve_tool = tool("retrieve_parent_chunks")(self._retrieve_parent_chunks)

        return [search_tool, retrieve_tool]
