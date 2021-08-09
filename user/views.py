from django.http.response import HttpResponseRedirect
from .models import MyUser
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.views.generic.base import TemplateView
from .forms import MyAuthenticationForm, SignupForm

# Create your views here.

class SignUpView(TemplateView):
    template_name = "user/signup.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        ## register user and redirect to login if failed, next (an url parameter) if successful
        next = request.GET.get('next', '/login/')
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']        
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']

            MyUser.objects.create_user(username=username, password=password, email=email)
            return HttpResponseRedirect(next + "?signup=True")
        else:
            return render(request, "user/signup.html", context={"form": form})


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        signup_form = SignupForm()
        context['form'] = signup_form
        return context


class MyLoginView(LoginView):
    template_name = "user/login.html"
    redirect_authenticated_user = True
    authentication_form = MyAuthenticationForm