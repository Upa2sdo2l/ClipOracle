from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'genres'

class Video(models.Model):
    video_text = models.TextField()
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    tags = models.CharField(max_length=255)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, related_name='videos')
    file_path = models.CharField(max_length=255)

    class Meta:
        db_table = 'videos'