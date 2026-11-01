from multiprocessing import AuthenticationError
from uuid import UUID
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
from supabase import create_client, Client 
from app.schemas.auth_model import LoginCredentials
from app.schemas.bookshelf_model import Status
from app.settings import settings
from typing import Dict, Any


user_client: Client = create_client(settings.supabase_url, settings.supabase_api_key)
catalog_client: Client = create_client(settings.supabase_url, settings.supabase_service_role_key)
security = HTTPBearer()

BOOK_COLS = "id,provider_book_id,title,subtitle,authors,description,genres,moods,tags,image,pages,release_year,rating"

def user_db(acecss_token: str) -> Client:
    c = create_client(settings.supabase_url, settings.supabase_api_key)
    c.postgrest.auth(acecss_token)
    return c

async def user_sign_up(username: str, password: str):
    user_data = user_client.auth.sign_up({
        'email': username,
        'password': password,
        # 'options': {
        #     'email_redirect_to': 'https://example.com/welcome',
        # },
    })
    
    return user_data


async def user_login(credentials: LoginCredentials):
    try: 
        response = user_client.auth.sign_in_with_password({
            'email': credentials.email,
            'password': credentials.password,
            })

        session = response.session
        user = response.user

        return { "user": user, "session": session }
        
    except AuthenticationError as e:
        raise HTTPException(status_code=400, detail={ user: None, session: None, e: str(e) })


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        response = user_client.auth.get_user(token)
        return response.user.id
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=e
        )

async def create_user_profile(id, first_name, last_name):
    user_profile = user_client.table('profiles').upsert({
        'id': id,
        'first_name': first_name,
        'last_name': last_name
    })

    return user_profile


def set_book_status_in_bookshelf(*, user_id: str, catalog_book: Dict[str, Any], status: Status, access_token: str) -> dict[str, Any]:
    stored_book = (
        catalog_client.table("books")
        .upsert(catalog_book, on_conflict="provider,provider_book_id")
        .execute()
        .data[0]
    )

    db = user_db(access_token)
    db.table("user_books").upsert(
        {"user_id": user_id, "book_id": stored_book["id"], "status" : status.value},
        on_conflict="user_id,book_id"
    ).execute()

    return (db.table("user_books")
        .select(f"*, books({BOOK_COLS})")
        .eq("user_id", user_id)
        .eq("book_id", stored_book["id"])
        .single()
        .execute()
        .data
        )
    

def set_ratings_in_bookshelf(*, user_id: str, access_token: str, rating: int | float| None, provider_book_id: str):
    db = user_db(access_token)
    book = (
        catalog_client.table("books")
        .select("id")
        .eq("provider", "hardcover")
        .eq("provider_book_id", provider_book_id)
        .limit(1)
        .execute()
        .data
    )
    if not book: 
        return None

    rows = (db.table("user_books")
        .update({"rating": rating})
        .eq("user_id", user_id)
        .eq("book_id", book[0]["id"])
        .execute()
        .data
        )
    
    return rows[0] if rows else None

  
def get_bookshelf(*, user_id: str, access_token: str):
    return (
        user_db(access_token)
        .table("user_books")
        .select(f"*, books({BOOK_COLS})")
        .eq("user_id", user_id)
        .order("updated_at", desc=True)
        .execute()
        .data
    )


def set_favorite_book(
        *, user_id: str, book_id: UUID, is_favorite: bool, access_token: str
        
):
    db = user_db(access_token)

    query = (
        user_client 
        .table("user_books")
        .update({"is_favorite": is_favorite})
        .eq("user_id", user_id)
        .eq("book_id", str(book_id))
        .select("*, books(*)")
        .execute()
    )

    return query.data[0] if query.data else None