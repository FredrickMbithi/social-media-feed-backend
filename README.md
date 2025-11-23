# Social Media Feed Backend - GraphQL API

Real-time social media feed backend with GraphQL API.

## Tech Stack

- Django 5.x
- PostgreSQL
- GraphQL (Graphene / graphene-django)
- Python 3.10+

## Setup

```bash
# Clone and setup
git clone <your-repo-url>
cd social-media-feed-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database setup
cp .env.example .env
# Edit .env with your credentials
createdb socialfeed_db || echo "Database already exists"
python manage.py migrate

# Seed test data
python manage.py seed_data

# Run server
python manage.py runserver
```

## GraphQL Playground

Access at: `http://localhost:8000/graphql/`

### Sample Queries

**List Posts:**

```graphql
query {
  posts(page: 1, perPage: 10) {
    id
    content
    likesCount
    author {
      username
    }
  }
}
```

**Get Single Post:**

```graphql
query {
  post(id: "1") {
    id
    content
    comments {
      content
      author {
        username
      }
    }
  }
}
```

## Current Status

✅ Day 1: Project setup, models, database schema  
✅ Day 2: GraphQL integration, queries working

## Next Steps

- Authentication (JWT)
- Mutations (create post, comment, like, share)
- Performance optimization

## Troubleshooting

| Issue                      | Fix                                                       |
| -------------------------- | --------------------------------------------------------- |
| No module named 'graphene' | `pip install graphene-django`                             |
| GraphiQL not loading       | Ensure CORS middleware added & csrf_exempt on GraphQLView |
| Empty query results        | Run `python manage.py seed_data`                          |
| DB connection errors       | Check Postgres is running (`pg_isready`) & .env values    |

## Development Notes

- Uses `select_related` / `prefetch_related` for ORM efficiency.
- Denormalized counters (`likes_count`, `comments_count`, `shares_count`) maintained during interactions.

## Roadmap

Day 3: JWT auth & protected mutations  
Day 4: Reactions, pagination refinements, N+1 audit  
Day 5: Caching & performance metrics

## License

MIT (add LICENSE file if missing)
