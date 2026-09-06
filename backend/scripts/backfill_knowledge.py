from app.db.session import SessionLocal
from app.services.knowledge.backfill import KnowledgeBackfillService


def main() -> None:

    db = SessionLocal()

    try:

        service = KnowledgeBackfillService()

        result = service.process_all_documents(
            db=db
        )

        print("KNOWLEDGE BACKFILL COMPLETE")
        print(
            f"Documents processed: "
            f"{result['documents_processed']}"
        )
        print(
            f"Chunks processed: "
            f"{result['chunks_processed']}"
        )
        print(
            f"Entities created/updated: "
            f"{result['entities']}"
        )
        print(
            f"Claims created: "
            f"{result['claims']}"
        )
        print(
            f"Events created: "
            f"{result['events']}"
        )
        print(
            f"Relationships created: "
            f"{result['relationships']}"
        )
        print(
            f"Evidence created: "
            f"{result['evidence']}"
        )

        for document in result["documents"]:

            print(
                f"\n{document['document_title']}"
            )

            print(
                f"  chunks={document['chunks_processed']}"
                f" entities={document['entities']}"
                f" claims={document['claims']}"
                f" events={document['events']}"
                f" relationships={document['relationships']}"
                f" evidence={document['evidence']}"
            )

    finally:

        db.close()


if __name__ == "__main__":
    main()