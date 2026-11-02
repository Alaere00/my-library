import sys
from app.dbs.supabase_db import catalog_client
from app.services.embeddings.embeddings import weight
from app.services.recommendation.recommendations import get_recommendation

user_id = sys.argv[1]

shelf = (
    catalog_client.table("user_books")
    .select("status,is_favorite,rating,books(title,genres,authors,embedding)")
    .eq("user_id", user_id)
    .execute()
    .data
)
print("SHELF")
for r in shelf:
    b = r["books"]
    print(f"  w={weight(r):<4} embedded={b['embedding'] is not None!s:<5} "
          f"{r['status']:<17} fav={r['is_favorite']!s:<5} rating={r['rating']}  {b['title']}")

# what it recommends
result = get_recommendation(user_id, limit=25)
print(result)
print("\nRECOMMENDATIONS")
for i, h in enumerate(result, 1):
    print(f"  {i:>2}. {h.title} by {', '.join(h.author_names or [])}  {h.genres[:3] if h.genres else ''}")


