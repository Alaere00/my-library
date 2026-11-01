import re

search_query = """
query Search($q: String!, $page: Int!, $per_page: Int!){
    search(query: $q, query_type: "Book", per_page: $per_page, page: $page){
        results
    }
}
"""


title_query = """
query SearchBookByTitle($title: String!, $page: Int!, $per_page: Int!){
    search(
        query: $title, 
        query_type: "book",
        fields: "title",
        weights: "1",
        typos: "0",
        page: $page,
        per_page: $per_page
        ){
        results
    }
}
"""


author_query = """
query GetBookInfoByAuthor($slug: String!, $limit: Int!, $offset: Int!) {
    authors(where: {slug: {_eq: $slug}}, limit: 1) {
        id name slug bio books_count cached_image alternate_names identifiers
    }
    books_aggregate(where: {contributions: {author: {slug: {_eq: $slug}}}}) {
        aggregate { count }
    }
    contributions { author { name } }
    books(
        where: {contributions: {author: {slug: {_eq: $slug}}}}
        order_by: {users_count: desc}
        limit: $limit
        offset: $offset
    ) {
        id title slug subtitle description release_year cached_image cached_tags pages
    }
}
"""


isbn_query = """
query GetBookByISBN($isbn: String!) {
  books(
    where: {
      editions: {
        _or: [
          { isbn_13: { _eq: $isbn } },
          { isbn_10: { _eq: $isbn } }
        ]
      }
    }
    order_by: { users_count: desc }
    limit: 1
  ) {
    id
    title
    subtitle
    description
    pages
    rating
    ratings_count
    release_date
    release_year
    cached_image
    cached_tags
    contributions { contribution author { id name } }
    book_series(order_by: { featured: desc }) {
      position
      series { id name }
    }
    book_characters { character { id name } }
    editions { isbn_10 isbn_13 reading_format { format } }
  }
}
"""

def to_slug(author_name: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', author_name.lower()).strip('-')
