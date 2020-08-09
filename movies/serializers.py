from rest_framework import serializers

from .models import Movie, Genre


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