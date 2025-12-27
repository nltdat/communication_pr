from django.db import models

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    description = models.TextField()
    status = models.BooleanField(default=False)
    image = models.TextField()
    post_id = models.TextField()
