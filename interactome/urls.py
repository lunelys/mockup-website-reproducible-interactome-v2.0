# Author: Lunelys RUNESHAW <lunelys.runeshaw@etudiant.univ-rennes.fr>
# URL configuration for interactome project

from django.urls import path

from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'interactome'
urlpatterns = [
                  path('', views.index, name='index'),
                  path('search/', views.search, name='search'),
                  path('archive/', views.archive, name="archive"),
                  path('about/', views.about, name='about'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# https://docs.djangoproject.com/en/4.2/howto/static-files/#deployment
