import re

author_query = """
query GetBookInfoByAuthor($slug: String!){
    authors(where: {slug: {_eq: $slug}}, limit: 10){
        alternate_names	
        bio	
        books_count
        cached_image	
        gender_id	
        identifiers	
        image_id	
        is_bipoc	
        name
        name_personal	
        contributions(where: {contributable_type: {_eq: "Book"}}){
            book {
                title
                description
                release_year
                pages

            }
        }
    }
}
"""


def to_slug(author_name: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', author_name.lower()).strip('-')
