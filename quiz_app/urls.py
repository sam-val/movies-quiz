from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


from rest_framework.urlpatterns import format_suffix_patterns

app_name = "quiz_app"
urlpatterns = [
     path('', views.CategoryListView.as_view(), name='index'),
     path('profile/<str:username>',views.profile, name="profile"),
     path('check-quizz/<slug:cat_slug>', views.process_quizz, name="check_quizz"),
     path('quizz/<slug:slug>', views.QuestionListView.as_view(), name='quizz'),
     path('quizz/<slug:slug>/result', views.result, name='result'),
     path('api/category/', views.category_list, name='category_list'),
     path('api/category/<int:pk>', views.category_detail, name='category_detail'),
     path('api/question/', views.question_list, name='question_list'),
     path('api/question/<int:pk>', views.question_detail, name='question_detail'),
     path('api/points/', views.points_list, name='points_list'),
     path('api/points/<int:pk>', views.points_detail, name='points_detail'),
     path('api/answer/', views.answer_list, name='answer_list'),
     path('api/answer/<int:pk>', views.answer_detail, name='answer_detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)