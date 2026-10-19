from multiprocessing import AuthenticationError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
from supabase import create_client, Client 
from app.schemas.bookshelf_model import Status
from app.settings import settings
from typing import Dict, Any


user_client: Client = create_client(settings.supabase_url, settings.supabase_api_key, None)
catalog_client: Client = create_client(settings.supabase_url, settings.supabase_service_role_key)
security = HTTPBearer()

async def user_sign_up(username: str, password: str):
    user_data = user_client.auth.sign_up({
        'email': username,
        'password': password,
        # 'options': {
        #     'email_redirect_to': 'https://example.com/welcome',
        # },
    })
    
    return user_data


async def user_sign_in(username: str, password):
    try: 
        response = user_client.auth.sign_in_with_password({
            'email': username,
            'password': password,
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
    user_client.postgrest.auth(access_token)
    
    stored_book = (
        catalog_client
        .table("books")
        .upsert(
            catalog_book,
            on_conflict="provider,provider_book_id",
        )
        .select("id")
        .single()
        .execute()
        .data
    )

    save_shelf_entry = (
        user_client
        .table("user_books")
        .upsert(
            {
                "user_id": user_id,
                "book_id": stored_book["id"],
                "status": status.value
            },
            on_conflict="user_id,book_id"
        )
        .select("*, books(*)")
        .single()
        .execute()
        .data
    )

    return save_shelf_entry
    


def get_bookshelf(*, user_id: str, access_token: str):
    query = (
        user_client
        .table("user_books")
        .select("*, books(*)")
        .eq("user_id", user_id)
    )

    user_client.postgrest.auth(access_token)

    response = query.order("updated_at", desc=True).execute

    return response.data
