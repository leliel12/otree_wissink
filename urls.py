# urls.py
from django.conf.urls import url, include
from otree.default_urls import urlpatterns

urlpatterns.append(
    url(r'^ajax_political_convention/',
        include('political_convention.ajax', namespace="ajax_political_convention"))
)
