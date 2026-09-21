# my-library

A personal book library API built with FastAPI, featuring search and recommendation capabilities via the Google Books API.

## Getting Started

### Prerequisites

- Python 3.14+
- Conda
- A [Google Books API key](https://developers.google.com/books/docs/v1/using#APIKey)

### Environment Setup

1. Create and activate the conda environment:

   ```bash
   conda create --name my-library --file requirements.txt
   conda activate my-library
   ```

2. Create a `.env` file in the project root:

   ```
   GOOGLE_BOOKS_API_KEY=your_api_key_here
   ```

### Running the Server

```bash
uvicorn app.main:app --reload
```

The server will start at `http://127.0.0.1:8000`. The interactive API docs are available at `http://127.0.0.1:8000/docs`.

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/search?query=...` | Search books (coming soon) |
| GET | `/book/{book_title}` | Look up a book by title via Google Books API |

## License

MIT