from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assumption import Assumption
from app.models.claim import Claim
from app.models.decision import Decision
from app.models.decision_dependency import DecisionDependency
from app.models.decision_impact import DecisionImpact


class DecisionAnalyzer:

    def analyze(
        self,
        db: Session,
        decision_id: UUID,
    ) -> dict:

        decision = db.get(
            Decision,
            decision_id,
        )

        if decision is None:
            raise ValueError(
                "Decision not found."
            )

        dependencies = (
            db.execute(
                select(DecisionDependency)
                .where(
                    DecisionDependency.decision_id
                    == decision_id
                )
                .order_by(
                    DecisionDependency.created_at
                )
            )
            .scalars()
            .all()
        )

        # ---------------------------------------------------------
        # Deduplicated assumptions
        # ---------------------------------------------------------
        assumption_map = {}

        # ---------------------------------------------------------
        # Deduplicated claims
        # ---------------------------------------------------------
        claim_map = {}

        for dependency in dependencies:

            if dependency.assumption_id:

                assumption = db.get(
                    Assumption,
                    dependency.assumption_id,
                )

                if assumption:

                    assumption_map[
                        str(assumption.id)
                    ] = {
                        "id": str(
                            assumption.id
                        ),
                        "name": assumption.name,
                        "description": (
                            assumption.description
                        ),
                        "status": assumption.status,
                        "confidence": (
                            assumption.confidence
                        ),
                    }

            if dependency.claim_id:

                claim = db.get(
                    Claim,
                    dependency.claim_id,
                )

                if claim:

                    claim_map[
                        str(claim.id)
                    ] = {
                        "id": str(claim.id),
                        "predicate": (
                            claim.predicate
                        ),
                        "object_text": (
                            claim.object_text
                        ),
                        "normalized_value": (
                            claim.normalized_value
                        ),
                        "confidence": (
                            claim.confidence
                        ),
                        "valid_from": (
                            claim.valid_from.isoformat()
                            if claim.valid_from
                            else None
                        ),
                        "valid_until": (
                            claim.valid_until.isoformat()
                            if claim.valid_until
                            else None
                        ),
                    }

        # ---------------------------------------------------------
        # Existing impacts
        # ---------------------------------------------------------
        impacts = (
            db.execute(
                select(DecisionImpact)
                .where(
                    DecisionImpact.decision_id
                    == decision_id
                )
                .order_by(
                    DecisionImpact.created_at.desc()
                )
            )
            .scalars()
            .all()
        )

        severity_rank = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }

        highest_severity = "low"

        for impact in impacts:

            if severity_rank.get(
                impact.severity,
                2,
            ) > severity_rank.get(
                highest_severity,
                1,
            ):
                highest_severity = (
                    impact.severity
                )

        if highest_severity in {
            "high",
            "critical",
        }:
            status = "review_required"

        elif impacts:
            status = "monitor"

        else:
            status = decision.status

        return {
            "decision": {
                "id": str(decision.id),
                "title": decision.title,
                "description": (
                    decision.description
                ),
                "status": status,
                "priority": decision.priority,
                "confidence": decision.confidence,
            },
            "impact_level": highest_severity,
            "impacted_assumptions": list(
                assumption_map.values()
            ),
            "impacted_claims": list(
                claim_map.values()
            ),
            "impacts": [
                {
                    "id": str(impact.id),
                    "impact_type": (
                        impact.impact_type
                    ),
                    "severity": impact.severity,
                    "explanation": (
                        impact.explanation
                    ),
                    "confidence": (
                        impact.confidence
                    ),
                }
                for impact in impacts
            ],
        }