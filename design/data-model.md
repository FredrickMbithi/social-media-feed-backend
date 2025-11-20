# Data Model

## Core Entities

### User (Django Auth)

- id, username, email, password (hashed)
- created_at, updated_at

### Post

- id, author (FK User), content (text), image_url (optional)
- created_at, updated_at
- likes_count, comments_count, shares_count (denormalized)
- **Indexes**: created_at DESC, author_id

### Comment

- id, post (FK), author (FK User), content
- created_at
- **Index**: (post_id, created_at DESC)

### Interaction

- id, post (FK), user (FK), interaction_type (like/share)
- created_at
- **Unique constraint**: (post_id, user_id, interaction_type)
- **Index**: (post_id, interaction_type)
