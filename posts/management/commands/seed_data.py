from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from posts.models import Post, Comment, Interaction
from faker import Faker
import random

fake = Faker()


class Command(BaseCommand):
    help = "Seeds database with test data"

    def handle(self, *args, **kwargs):
        # Create users
        self.stdout.write("Creating users...")
        users = []
        for i in range(5):
            user, created = User.objects.get_or_create(
                username=f"user{i+1}",
                defaults={
                    "email": f"user{i+1}@example.com",
                },
            )
            if created:
                user.set_password("password123")
                user.save()
            users.append(user)

        self.stdout.write(self.style.SUCCESS(f"Created {len(users)} users"))

        # Create posts
        self.stdout.write("Creating posts...")
        posts = []
        for i in range(20):
            post = Post.objects.create(
                author=random.choice(users),
                content=fake.text(max_nb_chars=200),
                image_url=fake.image_url() if random.choice([True, False]) else None,
            )
            posts.append(post)

        self.stdout.write(self.style.SUCCESS(f"Created {len(posts)} posts"))

        # Create comments
        self.stdout.write("Creating comments...")
        comment_count = 0
        for post in posts:
            for _ in range(random.randint(1, 5)):
                Comment.objects.create(
                    post=post, author=random.choice(users), content=fake.sentence()
                )
                comment_count += 1
                post.comments_count += 1
            post.save()

        self.stdout.write(self.style.SUCCESS(f"Created {comment_count} comments"))

        # Create interactions
        self.stdout.write("Creating interactions...")
        interaction_count = 0
        for post in posts:
            # Random likes
            like_users = random.sample(users, k=random.randint(1, len(users)))
            for user in like_users:
                Interaction.objects.get_or_create(
                    post=post, user=user, interaction_type="like"
                )
                interaction_count += 1
                post.likes_count += 1

            # Random shares
            if random.choice([True, False]):
                share_user = random.choice(users)
                Interaction.objects.get_or_create(
                    post=post, user=share_user, interaction_type="share"
                )
                interaction_count += 1
                post.shares_count += 1

            post.save()

        self.stdout.write(
            self.style.SUCCESS(f"Created {interaction_count} interactions")
        )
        self.stdout.write(self.style.SUCCESS("✅ Database seeded successfully!"))
