from typing import List, Dict, Any


class ReciprocalRankFusion:
    def __init__(self, k_constant: int = 60):
        # 60 is the standard smoothing constant recommended by research (Moffat & Zobel)
        self.k = k_constant

    def merge(
        self,
        semantic_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Combines results from semantic and keyword searches using the RRF algorithm."""
        rrf_scores: Dict[str, float] = {}
        payloads: Dict[str, Dict[str, Any]] = {}

        # 1. Process Semantic Results Rank
        for rank, hit in enumerate(semantic_results):
            # Unique identifier is Qdrant vector point ID (string format)
            point_id = str(hit["id"])
            payloads[point_id] = hit["payload"]
            
            # Add RRF score component: 1 / (k + rank)
            rrf_scores[point_id] = rrf_scores.get(point_id, 0.0) + (1.0 / (self.k + (rank + 1)))

        # 2. Process Keyword Results Rank
        for rank, hit in enumerate(keyword_results):
            point_id = str(hit["id"])
            if point_id not in payloads:
                payloads[point_id] = hit["payload"]
                
            rrf_scores[point_id] = rrf_scores.get(point_id, 0.0) + (1.0 / (self.k + (rank + 1)))

        # 3. Sort candidates by score descending
        sorted_candidates = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)

        # 4. Formulate top-k unified response list
        merged_results = []
        for point_id, score in sorted_candidates:
            merged_results.append({
                "id": point_id,
                "score": round(score, 6),
                "payload": payloads[point_id]
            })

        return merged_results
