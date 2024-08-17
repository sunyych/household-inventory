from django.db import models

class InventoryItem(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    expiration_date = models.DateField()

    def __str__(self):
        return self.name