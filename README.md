# Social Media Feed Backend - GraphQL API

Real-time social media feed backend with GraphQL API.

## Tech Stack

- Django 4.2+
- PostgreSQL
- GraphQL (Graphene)
- Python 3.10+

## Setup

\`\`\`bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Edit .env with your database credentials

python manage.py migrate
python manage.py runserver
\`\`\`

## Current Status

✅ Day 1: Project setup, models, database schema

## Next Steps

- GraphQL integration
- Authentication
- API implementation
