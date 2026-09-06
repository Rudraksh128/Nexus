from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.assumption import Assumption
from app.models.claim import Claim
from app.models.chunk import DocumentChunk
from app.models.decision import Decision
from app.models.decision_impact import DecisionImpact
from app.models.document import Document
from app.models.entity import Entity
from app.models.event import Event
from app.models.evidence import Evidence
from app.models.relationship import EntityRelationship


class AnalyticsService:

    def workspace_summary(
        self,
        db: Session,
        workspace_id: UUID,
    ) -> dict:

        def count(model):
            return db.execute(
                select(
                    func.count()
                ).select_from(model).where(
                    model.workspace_id
                    == workspace_id
                )
            ).scalar() or 0

        # Models containing workspace_id.
        documents = count(Document)
        entities = count(Entity)
        claims = count(Claim)
        events = count(Event)
        relationships = count(
            EntityRelationship
        )
        decisions = count(Decision)
        assumptions = count(Assumption)

        # Chunks require a join through pages.
        from app.models.page import DocumentPage

        chunks = db.execute(
            select(
                func.count()
            )
            .select_from(DocumentChunk)
            .join(
                DocumentPage,
                DocumentChunk.page_id
                == DocumentPage.id,
            )
            .join(
                Document,
                DocumentPage.document_id
                == Document.id,
            )
            .where(
                Document.workspace_id
                == workspace_id
            )
        ).scalar() or 0

        # Evidence is linked to claims rather than
        # directly to workspaces.
        evidence = db.execute(
            select(
                func.count()
            )
            .select_from(Evidence)
            .join(
                Claim,
                Evidence.claim_id
                == Claim.id,
            )
            .where(
                Claim.workspace_id
                == workspace_id
            )
        ).scalar() or 0

        # Decision impacts are linked through decisions.
        impacts = db.execute(
            select(
                func.count()
            )
            .select_from(DecisionImpact)
            .join(
                Decision,
                DecisionImpact.decision_id
                == Decision.id,
            )
            .where(
                Decision.workspace_id
                == workspace_id
            )
        ).scalar() or 0

        return {
            "workspace_id": str(
                workspace_id
            ),
            "documents": documents,
            "chunks": chunks,
            "entities": entities,
            "claims": claims,
            "evidence": evidence,
            "events": events,
            "relationships": relationships,
            "assumptions": assumptions,
            "decisions": decisions,
            "decision_impacts": impacts,
        }