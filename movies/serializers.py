from django.contrib.auth import authenticate
from django.core import exceptions
from rest_framework import serializers

from .models import Movie, Genre, Watchlist, Watchedlist


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(read_only=True, many=True)
    class Meta:
        model = Movie

        fields = [
            'id',
            'name',
            'imdb_score',
            'popularity',
            'director',
            'genres',
        ]


class WatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = [
            'movies'
        ]

class WatchedlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchedlist
        fields = [
            'movies'
        ]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get("username", "")
        password = data.get("password", "")

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data["user"] = user
                else:
                    msg = "User is deactivated."
                    raise exceptions.ValidationError(msg)
            else:
                msg = "Unable to login with given credentials."
                raise exceptions.ValidationError(msg)
        else:
            msg = "Must provide username and password both."
            raise exceptions.ValidationError(msg)
        return data