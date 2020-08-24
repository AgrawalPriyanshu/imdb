from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet

from movies.models import Movie, Watchlist, Watchedlist, Genre
from movies.serializers import MovieSerializer, WatchlistSerializer, WatchedlistSerializer

import requests
from bs4 import BeautifulSoup
import json



class MovieViewset(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    lookup_field = 'pk'

    @action(detail=False, methods=['POST'])
    def update_database(self, request):
        URL = request.data["url"]
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, 'html.parser')
        results = soup.find_all('td', class_="posterColumn")
        link_list = []
        for result in results:
            link = result.find('a')['href']
            link_list.append(link)

        movie_list = []
        for link in link_list:
            mv_url = 'https://www.imdb.com/' + link
            mv_page = requests.get(mv_url)
            mv_soup = BeautifulSoup(mv_page.content, 'html.parser')
            mv_names = mv_soup.find_all('h1', class_="")
            if mv_names == []:
                continue
            mv_name = mv_names[0].text
            mv_ratings = mv_soup.find_all('span', class_="rating")
            if mv_ratings == []:
                mv_rating = 5
            else:
                mv_rating = mv_ratings[0].text
            mv_genres = mv_soup.find_all('div', class_="see-more inline canwrap")
            mv_genres = mv_genres[-1].text.split("|")
            genre_list = []
            for genre in mv_genres:
                g = genre[genre.index(" ") + 1:-1]
                genre_list.append(g)
            d = {'movie_name': mv_name, 'rating': mv_rating, 'genres': genre_list}
            movie_list.append(d)

            mv, created = Movie.objects.get_or_create(name=mv_name, imdb_score=float(mv_rating.split('/')[0]),
                                                      popularity=float(mv_rating.split('/')[0]) * 10)
            if created:
                mv.save()
            for g in genre_list:
                gnr, is_created = Genre.objects.get_or_create(genre=g)
                if is_created:
                    gnr.save()
                    mv.genres.add(gnr)
                else:
                    mv.genres.add(gnr)
        return Response(json.dumps(movie_list))

    @action(detail=False)
    def search_movie(self, request):
        keyword = request.GET.get('q', '')
        queryset = Movie.objects.filter(name__icontains=keyword)
        serializer = MovieSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def get_watchlist(self, request):
        keyword = request.GET.get('q', '')
        queryset = Watchlist.objects.filter(users=request.user).values_list('movies')
        movie_id = [i[0] for i in queryset]
        movies = Movie.objects.filter(id__in=movie_id)
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def get_watchedlist(self, request):
        keyword = request.GET.get('q', '')
        queryset = Watchedlist.objects.filter(users=request.user).values_list('movies')
        movie_id = [i[0] for i in queryset]
        movies = Movie.objects.filter(id__in=movie_id)
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def add_to_watch(self, request):
        serializer = WatchlistSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            movie_obj = serializer.validated_data.get('movies')
            obj, created = Watchlist.objects.get_or_create(
                users=user
            )
            if created:
                obj.save()
            try:
                obj.movies.add(movie_obj[0])
            except Exception as e:
                return HttpResponse(content={'error': e})
            return Response(serializer.data)
        else:
            return Response({"msg": "movie not found with this id"}, status=status.HTTP_204_NO_CONTENT, headers=None)

    @action(detail=False, methods=['POST'])
    def mark_watched(self, request):
        serializer = WatchedlistSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            movie_obj = serializer.validated_data.get('movies')
            obj, created = Watchedlist.objects.get_or_create(
                users=user
            )
            if created:
                obj.save()
            try:
                obj.movies.add(movie_obj[0])
            except Exception as e:
                return HttpResponse(content={'error': e})
            return Response(serializer.data)
        else:
            return Response({"msg": "movie not found with this id"}, status=status.HTTP_204_NO_CONTENT, headers=None)

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        serializer_action_classes = {
            'create': MovieSerializer,
            'update': MovieSerializer,
            'partial_update': MovieSerializer,
            'retrieve': MovieSerializer
        }
        if hasattr(self, 'action'):
            return serializer_action_classes.get(self.action, self.serializer_class)
        return self.serializer_class

    """
        Create a model instance.
    """

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser:

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({"msg": "not permitted to perform this action"}, status=status.HTTP_403_FORBIDDEN, headers=None)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def get_object(self):

        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    """
        Update a model instance.
    """

    def update(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"msg": "not permitted to perform this action"}, status=status.HTTP_403_FORBIDDEN,
                            headers=None)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    """
    Destroy a model instance.
    """

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"msg": "not permitted to perform this action"}, status=status.HTTP_403_FORBIDDEN,
                            headers=None)
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

