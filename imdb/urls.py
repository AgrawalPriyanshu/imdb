"""imdb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

# from movies.api import MoviesView
from rest_framework_swagger.views import get_swagger_view

from movies.routers import router
from movies.views import LoginView, LogoutView

schema_view = get_swagger_view(title='IMDB APIs')

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('add_movie/', MoviesView.as_view()),
    path('api/', include(router.urls)),
    url(r'^docs/', schema_view),
    path('api/v1/auth/login/', LoginView.as_view()),
    path('api/v1/auth/logout/', LogoutView.as_view()),
    path('rest-auth/registration/', include('rest_auth.registration.urls')),

]
