from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField('self', symmetrical=False)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='subs')
    joined = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.username   

    def serialize(self):
        return {
            "id": self.id,
            "following": [user.username for user in self.following.all()],
            "followers": [user.username for user in self.followers.all()],
        }

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    likes = models.ManyToManyField(User)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"#{self.id} from {self.author}"

    class Meta:
        ordering = ['-timestamp']

    def serialize(self):
        return {
            "id": self.id,
            "likes": [] if not self.likes else [user.username for user in self.likes.all()],
        }

    

