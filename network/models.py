from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    like_count = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.content[0:50]


class Following(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    followed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_post = models.ForeignKey(Post, on_delete=models.CASCADE)

""" 
Posts
    User
    Content
    Like_count
    Date
"""

"""
Following
    User
    followed_user
"""