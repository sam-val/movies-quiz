from datetime import datetime, time, timedelta
from django.conf import settings
from django.contrib import auth
import sys
from datetime import datetime, timedelta
import json

class ResetSession:
    def __init__(self, get_response):
        self.get_response = get_response    

    def __call__(self, request):
        now = datetime.now().timestamp()
        last_touched = request.session.get('last_touched', None)
        if last_touched:
            if now > last_touched + settings.SESSION_EXPIRATION_SECS:
                if request.user.is_authenticated:
                    auth.logout(request)
                else:
                    request.session.flush()
        else: 
            request.session['last_touched'] = datetime.now().timestamp()


        response = self.get_response(request)
        return response