#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from political_convention import views

urlpatterns = [
    url(r'^kick_player/$', views.kick_player, name='kick_player'),
]
