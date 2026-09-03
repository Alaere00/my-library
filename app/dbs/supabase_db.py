import uuid
from supabase import create_client, Client 
from app.settings import settings


supabase: Client = create_client(settings.supabase_url, settings.supabase_api_key, None)

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
    user_data = supabase.auth.sign_in_with_password({
        'email': username,
        'password': password,
        })
    
    return user_data


def book_shelf(user_id: uuid, book_title: str, book_isbn):
    supabase.table('user_book_status').upsert({
        'user_id': user_id, 
        'book_title': book_title,
        'isbn': book_isbn
    })

    return 


# these can be refactored into one db
def set_reading_status():
    pass


async def update_reading_status():
    pass



async def update_favorites():
    pass

