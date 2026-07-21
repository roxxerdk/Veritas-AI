import re
from typing import List, Dict, Any, Tuple


class CitationAgent:
    def format_citations(
        self,
        answer: str,
        relevant_chunks: List[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Parses inline reference tags, maps them to sources, and appends citations payload."""
        if not answer or not relevant_chunks:
            return answer, []

        citations = []
        formatted_answer = answer
        
        # Regex patterns to search for tags: [chunk_12] or [Source index: 0]
        # Match standard brackets like [chunk_1] or [chunk_uuid] or [Source index: 0]
        pattern = re.compile(r"\[(?:Source index:\s*(\d+)|chunk_(\w+))\]")
        matches = pattern.findall(answer)
        
        # Keep track of unique source hits and map them to sequential citation indices [1], [2], etc.
        unique_sources = []
        source_to_citation_index = {}

        for match in matches:
            idx_str, chunk_uuid = match
            source_index = None

            if idx_str:
                source_index = int(idx_str)
            elif chunk_uuid:
                # Find matching chunk index by matching chunk ID or vector UUID
                for i, hit in enumerate(relevant_chunks):
                    payload = hit.get("payload", {})
                    if str(payload.get("chunk_id")) == chunk_uuid or str(hit.get("id")) == chunk_uuid:
                        source_index = i
                        break
            
            if source_index is not None and 0 <= source_index < len(relevant_chunks):
                hit = relevant_chunks[source_index]
                point_id = str(hit.get("id"))
                
                if point_id not in unique_sources:
                    unique_sources.append(point_id)
                    citation_idx = len(unique_sources)
                    source_to_citation_index[point_id] = citation_idx
                    
                    payload = hit.get("payload", {})
                    citations.append({
                        "index": citation_idx,
                        "filename": payload.get("filename", "unknown"),
                        "page_number": payload.get("page_number", 1),
                        "snippet": payload.get("content", "")[:150] + "..."
                    })

        # Replace tags inside text with [1], [2], etc.
        def replace_tag(match):
            idx_str, chunk_uuid = match.groups()
            source_index = None

            if idx_str:
                source_index = int(idx_str)
            elif chunk_uuid:
                for i, hit in enumerate(relevant_chunks):
                    payload = hit.get("payload", {})
                    if str(payload.get("chunk_id")) == chunk_uuid or str(hit.get("id")) == chunk_uuid:
                        source_index = i
                        break

            if source_index is not None and 0 <= source_index < len(relevant_chunks):
                hit = relevant_chunks[source_index]
                point_id = str(hit.get("id"))
                citation_num = source_to_citation_index.get(point_id)
                if citation_num:
                    return f"[{citation_num}]"
            
            return match.group(0)

        formatted_answer = pattern.sub(replace_tag, answer)
        
        # Sort citations index by sequence numbering
        citations = sorted(citations, key=lambda c: c["index"])

        return formatted_answer, citations
