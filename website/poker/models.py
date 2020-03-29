from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Room(models.Model):
    name = models.CharField(max_length=20)
    max_people = models.IntegerField(default=6)
    bot_num = models.IntegerField(default=0)
    start = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name) + " " + str(self.max_people)

class Room_Person(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    person = models.ForeignKey(User, on_delete=models.CASCADE)
    seq_id = models.IntegerField(default=0)
    
    def __str__(self):
        return str(self.room) + " " + self.person.username