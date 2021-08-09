from enum import unique
from django.contrib.auth.forms import UserModel
from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import HiddenInput
from django.utils.text import slugify
from django.db.models.fields import BooleanField, CharField, IntegerField, TextField
from django.conf import settings
# Create your models here.
from collections import namedtuple
import random
# Catpoints(cat, points):
# where cat == id of Category and points is points of this cat

CatPoints = namedtuple('CatPoints', ['cat', 'points'])

class QuizForm(forms.Form):

    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        # print(f"kwargs: {type(kwargs)}")
        super().__init__(*args, **kwargs)
        self.fields['questions_length'] = forms.IntegerField(label="", widget=HiddenInput(attrs={'value':len(questions), 'read_only': True}))

        for i, q in enumerate(questions):
            self.fields[f'question_{i}'] = forms.CharField(label=q.question_text,
                                                           required=True,
                                                           widget=forms.RadioSelect(
                                                               choices=[(answer.id, answer.answer_text) for answer in sorted(q.answers.all(), key= lambda x: random.random())],
                                                            attrs={'class': "no-bullets"}
                                                           ))


class Category(models.Model):
    name = models.CharField(verbose_name="Category's Name", max_length=50)
    slug = models.SlugField(unique=True, max_length=255, null=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class UserPoints(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, blank=False)
    cat = models.ForeignKey(Category, verbose_name="Category",
                            on_delete=models.SET_NULL, null=True, blank=False)
    points = IntegerField("Points")

    class Meta:
        unique_together = ['user', 'cat']

    def __repr__(self) -> str:
        return f"User:{self.user.username}; Category: {self.cat.name}; Points: {self.points}"

class Question(models.Model):
    question_text = TextField(null=False, blank=False)

    cat = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)

    def __str__(self) -> str:
        return self.question_text


class Answer(models.Model):
    answer_text = CharField(max_length=200, blank=False, null=False)
    correct = BooleanField(default=False, blank=True)
    question = models.ForeignKey(
        Question, related_name='answers', on_delete=models.CASCADE, null=True)

    def __str__(self) -> str:
        return self.answer_text
