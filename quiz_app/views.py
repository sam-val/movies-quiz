from functools import partial
from typing import List
from django.contrib.auth.views import LoginView
from django.http.response import HttpResponseRedirect, JsonResponse
from quiz_app.models import Category, Question, UserPoints, Answer
from .serializers import CategorySerializer, QuestionReadSerializer, QuestionPatchSerializer, QuestionWriteSerializer, UserPointsSerializer, \
    AnswerWriteSerializer, AnswerReadSerializer, AnswerPatchSerializer

from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework.reverse import reverse
from django.views.generic import ListView
from .models import QuizForm, CatPoints
from .utils import session_points_exist

import random
# Create your views here.


def calculate_points(answers):
    return Answer.objects.filter(pk__in=answers, correct=True).count()



class HasNotAnsweredMixin:
    def dispatch(self, request, *args, **kwargs):
        ## check if unauthorized user has points in session or if authrized user has points in database
        valid = False
        if "cat_points" in request.session:
            if self.kwargs['slug'] in request.session['cat_points']:
                valid = True

        if valid:
            points = request.session['cat_points'][f"{self.kwargs['slug']}"]
            # question_length = len(self.get_queryset())
            return render(request, template_name="quiz_app/result.html", context={'corrects': points})
            # return HttpResponse(f"You already answered this category -- {points}/10 correctly. Points so far: {request.session['points_sofar']}")

        return super().dispatch(request, *args, **kwargs)

class QuestionListView(HasNotAnsweredMixin,ListView):
    paginate_by = 2
    model = Question
    context_object_name = 'questions'
    template_name = 'quiz_app/category_quiz.html'

    def get_queryset(self):
        return super().get_queryset().filter(cat__slug=self.kwargs['slug']).prefetch_related('answers')

    def get_context_data(self, **kwargs):
        questions = list(self.get_queryset()[:10])
        random.shuffle(questions)
        form = QuizForm(questions=questions)
        context = super().get_context_data(**kwargs)
        context['form'] = form
        if questions:
            context['category'] = questions[0].cat.name
        return context


class CategoryListView(ListView):
    model = Category
    title = 'index page'
    context_object_name = 'cats'
    template_name = 'quiz_app/index.html'

    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = self.title
        return context



def profile(request, username):
    pass

def result(request, slug):
    try:
        ## if cat_points is not in session redirect back to questions
        corrects = request.session['cat_points'][slug]
        question_len = request.GET['question_len']
    except KeyError:
        return HttpResponseRedirect(reverse('quiz_app:quizz', kwargs={'slug': slug}))
    return render(request, 'quiz_app/result.html', context={'corrects': corrects, 'question_len': question_len
    })

def process_quizz(request, cat_slug):
    """
    session['cat_points] is an dictionary with key == cat.slug and value == the points
    """
    # calculate points and redirect to index page 

    question_len = request.POST['questions_length']
    ## points in the session so far
    if session_points_exist(request):
        points_sofar = request.session['points_sofar']
    else:
        points_sofar = 0
        request.session['cat_points'] = dict() 


    # calculate points for this cat
    answers = []
    for key,item in request.POST.items():
        if key.startswith('question_'):
            answers.append(item)

    correct_answers = calculate_points(answers)

    ## update session
    request.session['cat_points'][f"{cat_slug}"] =  correct_answers
    request.session['points_sofar'] = points_sofar + correct_answers

    if request.user.is_authenticated:
        cat = Category.objects.filter(slug=cat_slug).first()
        UserPoints.objects.create(user=request.user,cat=cat,points=correct_answers)

    return HttpResponseRedirect(reverse(f'quiz_app:result', kwargs={'slug': cat_slug}) + f"?question_len={question_len}")
# API:


@api_view(['GET'])
def api_root(request, format=None):
    return Response({

    })

# CATEGORY:
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def category_list(request):
    """
    List/Add one or more categories
    """
    if request.method == "GET":
        try:
            cats = Category.objects.filter(name__icontains=request.GET['name'])
        except KeyError:
            cats = Category.objects.all()

        serializer = CategorySerializer(cats, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        data = JSONParser().parse(request)
        serializer = CategorySerializer(
            data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", 'DELETE'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def category_detail(request, pk):
    """
    Get, update or delete a category
    """

    try:
        cat = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = CategorySerializer(cat)
        return Response(serializer.data)
    elif request.method == "PUT":
        data = JSONParser().parse(request)
        serializer = CategorySerializer(cat, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            # 400 is client error 'cause their form/request not having correct info
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        cat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# USERPOINTS:


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def points_list(request):
    """
    List/Add one or more points
    """
    if request.method == "GET":
        try:
            points = UserPoints.objects.filter(user=request.GET['user'])
        except KeyError:
            points = UserPoints.objects.all()

        serializer = UserPointsSerializer(points, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        data = JSONParser().parse(request)
        serializer = UserPointsSerializer(
            data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", 'DELETE'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def points_detail(request, pk):
    """
    Get, update or delete a user points for a category with PK = user.id
    """

    try:
        points = UserPoints.objects.get(pk=pk)
    except UserPoints.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = UserPointsSerializer(points)
        return Response(serializer.data)
    elif request.method == "PUT":
        data = JSONParser().parse(request)
        serializer = UserPointsSerializer(points, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            # 400 is client error 'cause their form/request not having correct info
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        points.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def question_list(request, format=None):
    if request.method == "GET":
        questions = Question.objects.all()

        for key, values in request.GET.lists():
            for v in values:
                questions = questions.filter(**{key: v})


        serializer = QuestionReadSerializer(
            questions, many=True, context={'request': request})
        return Response(data=serializer.data)
    elif request.method == "POST":
        data = JSONParser().parse(request)
        serializer = QuestionWriteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def question_detail(request, pk, format=None):
    try:
        question = Question.objects.get(pk=pk)
    except Question.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = QuestionReadSerializer(
            question, context={'request': request})
        return Response(serializer.data)
    elif request.method == "PATCH":
        put_data = JSONParser().parse(request)

        # pass in the instance so the serializer.save() will call update(), not create()

        serializer = QuestionPatchSerializer(instance=question, data=put_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def answer_list(request):
    """
    List/Add an answer
    """
    if request.method == "GET":
        answers = Answer.objects.all()
        for key, values in request.GET.lists():
            for v in values:
                answers = answers.filter(**{key: v})
        print(answers)
        serializer = AnswerReadSerializer(
            answers, many=True, context={'request': request})
        return Response(serializer.data)
    elif request.method == "POST":
        data = JSONParser().parse(request)
        serializer = AnswerWriteSerializer(
            data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PATCH", 'DELETE'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def answer_detail(request, pk):
    """
    Get, update or delete an answer
    """

    try:
        answer = Answer.objects.get(pk=pk)
    except Answer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = AnswerReadSerializer(answer, context={"request": request})
        return Response(serializer.data)
    elif request.method == "PATCH":
        data = JSONParser().parse(request)
        serializer = AnswerPatchSerializer(answer, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            # 400 is client error 'cause their form/request not having correct info
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        answer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
