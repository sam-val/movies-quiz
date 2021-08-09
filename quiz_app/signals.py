from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import Category, UserPoints
from .utils import session_points_exist

from django.db import IntegrityError

@receiver(user_logged_in)
def post_login(sender, request, user, **kwargs):
    print("Running post_login")
    if session_points_exist(request):
        ## go through each category in session if session points exist
        ## if cat doesn't exist in database, create it; if cat already exists, override what is in database
        ## then pull userpoints from database and put it to session

        for slug,points in request.session['cat_points'].items():
            cat = Category.objects.filter(slug=slug).first()
            if not UserPoints.objects.filter(user=user, cat=cat).exists():
                UserPoints.objects.create(user=user, cat=cat, points=points)


    ## update session with points in database 
    user_points = UserPoints.objects.filter(user=user)
    request.session['cat_points'] = dict()
    points_sofar = 0
    for points in user_points:
        request.session['cat_points'][f"{points.cat.slug}"] = points.points
        points_sofar += points.points

    request.session['points_sofar'] = points_sofar        

@receiver(user_logged_out)
def post_logout(sender, request, user, **kwargs):
    print("Running post_logout")
    if session_points_exist(request):
        del request.session['cat_points']
        del request.session['points_sofar']