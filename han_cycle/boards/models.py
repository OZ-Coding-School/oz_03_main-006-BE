from django.db import models

class Board(models.Model):
    title = models.CharField(max_length=200, null=False)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)
    travel_start_date = models.DateField(null=True, blank=True)
    travel_end_date = models.DateField(null=True, blank=True)

    likes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
