from typing import Any


class EvidenceVerifier:

    def verify(
        self,
        question: str,
        tool_results: list[Any],
    ) -> dict[str, Any]:

        evidence: list[dict[str, Any]] = []

        for result in tool_results:

            if not result.success:
                continue

            data = result.data

            if not isinstance(data, dict):
                continue

            # ---------------------------------------------------------
            # Document evidence produced by the search tool
            # ---------------------------------------------------------
            search_results = data.get("results", [])

            if isinstance(search_results, list):

                for item in search_results:

                    if not isinstance(item, dict):
                        continue

                    text = str(item.get("text", "")).strip()

                    if not text:
                        continue

                    document_id = item.get("document_id")
                    document_title = item.get("document_title")
                    page_number = item.get("page_number")

                    # A document citation is considered valid only when
                    # the source metadata exists.
                    if not document_id or not document_title:
                        continue

                    evidence.append(
                        {
                            "source_type": "document",
                            "document_id": str(document_id),
                            "document_title": str(document_title),
                            "page_number": (
                                int(page_number)
                                if page_number is not None
                                else None
                            ),
                            "text": text,
                            "relevance": item.get("rerank_score"),
                            "tool": result.tool,
                        }
                    )

            # ---------------------------------------------------------
            # Structured claims produced by the knowledge tool
            # ---------------------------------------------------------
            claims = data.get("claims", [])

            if isinstance(claims, list):

                for claim in claims:

                    if not isinstance(claim, dict):
                        continue

                    predicate = str(
                        claim.get("predicate", "")
                    ).strip()

                    value = str(
                        claim.get("object_text")
                        or claim.get("normalized_value")
                        or ""
                    ).strip()

                    if not predicate or not value:
                        continue

                    evidence.append(
                        {
                            "source_type": "knowledge_claim",
                            "document_id": None,
                            "document_title": None,
                            "page_number": None,
                            "text": f"{predicate}: {value}",
                            "relevance": claim.get("confidence"),
                            "tool": result.tool,
                            "metadata": claim,
                        }
                    )

            # ---------------------------------------------------------
            # Events produced by timeline
            # ---------------------------------------------------------
            events = data.get("events", [])

            if isinstance(events, list):

                for event in events:

                    if not isinstance(event, dict):
                        continue

                    description = str(
                        event.get("description", "")
                    ).strip()

                    if not description:
                        continue

                    evidence.append(
                        {
                            "source_type": "event",
                            "document_id": None,
                            "document_title": None,
                            "page_number": None,
                            "text": description,
                            "relevance": event.get("confidence"),
                            "tool": result.tool,
                            "metadata": event,
                        }
                    )

        # -------------------------------------------------------------
        # Remove duplicate evidence
        # -------------------------------------------------------------
        unique: dict[tuple, dict[str, Any]] = {}

        for item in evidence:

            key = (
                item.get("source_type"),
                item.get("document_id"),
                item.get("page_number"),
                item.get("text"),
            )

            if key not in unique:
                unique[key] = item

        evidence = list(unique.values())

        # -------------------------------------------------------------
        # Sort strongest evidence first
        # -------------------------------------------------------------
        evidence.sort(
            key=lambda item: (
                float(item["relevance"])
                if item.get("relevance") is not None
                else -999.0
            ),
            reverse=True,
        )

        # Keep the evidence payload manageable.
        evidence = evidence[:20]

        return {
            "has_evidence": bool(evidence),
            "evidence_count": len(evidence),
            "evidence": evidence,
        }