from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db.models import F


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    image_url = models.URLField(blank=True, null=True)

    # Denormalized counters
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["author", "-created_at"]),
        ]

    def __str__(self):
        return f"Post by {self.author.username}: {self.content[:50]}"

    def like(self, user):
        """Atomic like operation"""
        interaction, created = Interaction.objects.get_or_create(
            post=self, user=user, interaction_type="like"
        )
        if created:
            Post.objects.filter(pk=self.pk).update(likes_count=F("likes_count") + 1)
            self.refresh_from_db()
        return self


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["post", "-created_at"]),
        ]


class Interaction(models.Model):
    INTERACTION_TYPES = [
        ("like", "Like"),
        ("share", "Share"),
    ]

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="interactions"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["post", "user", "interaction_type"]
        indexes = [
            models.Index(fields=["post", "interaction_type"]),
        ]
