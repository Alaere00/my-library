from multiprocessing import AuthenticationError

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
from supabase import create_client, Client 
from app.settings import settings


supabase: Client = create_client(settings.supabase_url, settings.supabase_api_key, None)
security = HTTPBearer()

async def user_sign_up(username: str, password: str):
    user_data = supabase.auth.sign_up({
        'email': username,
        'password': password,
        # 'options': {
        #     'email_redirect_to': 'https://example.com/welcome',
        # },
    })
    
    return user_data


async def user_sign_in(username: str, password):
    try: 

        response = supabase.auth.sign_in_with_password({
            'email': username,
            'password': password,
            })

        session = response.session
        user = response.user

        return { user: user, session: session }
        
    except AuthenticationError as e:
        raise HTTPException(status_code=400, detail={ user: None, session: None, e: str(e) })


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    print("token", token)
    try:
        response = supabase.auth.get_user(token)
        print("response", response)

        return response.user.id
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=e
        )

async def create_user_profile(id, first_name, last_name):
    user_profile = supabase.table('profiles').upsert({
        'id': id,
        'first_name': first_name,
        'last_name': last_name
    })

    return user_profile


def book_shelf(book_title: str, book_isbn):
    supabase.table('user_book_status').upsert({
        'book_title': book_title,
        'isbn': book_isbn
    })

    return 


# these can be refactored into one db
def set_reading_status():
    pass


async def update_reading_status():
    pass




async def ingest_searched_book_titles():
    pass