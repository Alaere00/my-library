from app.settings import settings
from sentence_transformers import SentenceTransformer
from supabase import create_client

supabase = create_client(settings.supabase_url, settings.supabase_api_key)

model = SentenceTransformer('BAAI/bge-large-en-v1.5')

# Mock data for testing purposes -> trying to figure out how to get the embeddings for the books in the database
books = [
    {"id": "book_01", "title": "The Chronicles of Eldoria", "authors": ["J.R. Roven"], "description": "An epic fantasy quest where a young elf must destroy a cursed ring to save the magical kingdom from an ancient dragon lord."},
    {"id": "book_02", "title": "Stars Beyond the Veil", "authors": ["Anya Vance", "Co-Author Name"], "description": "A hard sci-fi space opera featuring interstellar travel, artificial intelligence mutiny, and alien first contact on a distant exoplanet."},
    {"id": "book_03", "title": "Mindset of the Unstoppable", "authors": ["Dr. Marcus Vance"], "description": "A self-help and psychological guide to building daily discipline, breaking bad habits, and achieving professional success."},
    {"id": "book_04", "title": "Shadows over Baker Street", "authors": ["Arthur C. Doyle"], "description": "A classic detective mystery novel following a brilliant investigator solving a string of impossible locked-room murders in London."},
    {"id": "book_05", "title": "The Quantum Code", "authors": ["Liam Vance"], "description": "A fast-paced cyberpunk thriller about a rogue hacker who uncovers a government conspiracy hidden inside a quantum computing network."}
]

def get_book_embeddings():
    # """
    # Generate embeddings for a list of books using the SentenceTransformer model.

    # Args:
    #     books (list): A list of dictionaries, each containing book information.
    for book in books:
        # Step 1: Build text to embed in model for each book
        text_to_embed = f"Title {book['title']}. Authors: {', '.join(book['authors'])}. Description: {book['description']}"

        # Step 2: Generate the 1024-dimension vector
        embedding = model.encode(text_to_embed, normalize_embeddings=True).tolist()

        payload = {
            "id": book["id"],
            "title": book["title"],
            "authors": book["authors"],
            "embedding": embedding
        }

        try:
            supabase.table("items").insert(payload).execute()
        except Exception as e:
            print(f"Error inserting book {book['id']} into Supabase: {e}")

