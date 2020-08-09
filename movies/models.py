from django.db import models


# class User(models.Model):
#     email = models.CharField(max_length=50, primary_key=True)
#     first_name = models.CharField(max_length=30,default=None)
#     last_name = models.CharField(max_length=30, default=None)
#     gender = models.CharField(max_length=10, default=None)
#     phone_number = models.CharField(max_length=12)
#     city = models.CharField(max_length=50, default=None)
#     is_admin = models.BooleanField()
#     REQUIRED_FIELDS = ['phone_number','first_name','gender']
#
#     USERNAME_FIELD = 'email'
#
#     class Meta:
#         db_table = 'user'

class Genre(models.Model):
    genre = models.CharField(max_length=50)

    def __str__(self):
        return '{}'.format(self.genre)


class Movie(models.Model):
    name = models.CharField(max_length=100)
    imdb_score = models.FloatField()
    popularity = models.FloatField()
    director = models.CharField(max_length=100)
    genres = models.ManyToManyField(Genre)

    def __str__(self):
        return '{}'.format(self.name)

