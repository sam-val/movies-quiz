def session_points_exist(request):
    try:
        request.session['points_sofar']
        request.session['cat_points'] ## cat_points should be a dict
    except KeyError:
        ## if any other the two above doesn't exist
        ## one is enough, since they always go together
        return False
    return True
