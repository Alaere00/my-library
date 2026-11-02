from app.dbs.supabase_db import catalog_client
from app.services.embeddings.embeddings import build_text, embed_text

COLS = "id,title,subtitle,authors,genres,moods,tags,description"

def main():
    total = 0
    while True:
        rows = (
            catalog_client.table("books")
            .select(COLS)
            .is_("embedding", "null")
            .limit(100)
            .execute()
            .data
        )
        if not rows:
            break

        vectors = embed_text([build_text(r) for r in rows])
        for r, v in zip(rows, vectors):
            catalog_client.table("books").update({"embedding": v.tolist()}).eq("id", r["id"]).execute()
        total += len(rows)
        print("embedded", total)
    print("done")


main()