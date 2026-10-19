import re

search_query = """
query Search($q: String!, $page: Int!, $per_page: Int!){
    search(query: $q, query_type: "Book", per_page: $per_page, page: $page){
        results
    }
}
"""

title_query = """
query GetBookInfoByTitle($title: String!){
    books(where: {title: {_eq: $title}}, limit: 10){
        alternative_titles
        description
        featured_book_series {
            position
            series {
                name
                slug
            }
        }
        id
        image_id
        images {
            colors
            height
            id
            url
            width
        }
        pages
        release_date
        release_year
        slug
        title
        book_characters {
            character {
                name
            }
        }
        cached_contributors
        cached_featured_series
        cached_header_image
        cached_image
        cached_tags
        literary_type_id
        contributions {
            author {
                name
            }
        }
    }
}
"""

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

isbn_query = """
query GetEditionByISBN($isbn: String!) {
  editions(where: {FIELD: {_eq: $isbn }}) {
      id
      title
      subtitle
      isbn_13
      isbn_10
      asin
      pages
      release_date
      physical_format
      publisher {
          name
      }
      book {
          id
          title
          rating
          contributions {
              author {
                  name
              }
          }
      }
      language {
          language
      }
      reading_format {
          format
      }
  }
}
"""

def to_slug(author_name: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', author_name.lower()).strip('-')
