from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField, StringRelatedField
from .models import Category, UserPoints, Question, Answer


class QuestionRelatedField(serializers.RelatedField):

    def to_representation(self, question):
        return {'id': question.id, 'text': question.question_text}

class CatRelatedField(serializers.RelatedField):

    def to_representation(self, cat):
        return {'id': cat.id, 'slug': cat.slug}

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'id', 'slug']


class UserPointsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserPoints
        fields = ['id', 'user', 'points', 'cat']


class QuestionReadSerializer(serializers.ModelSerializer):
    # read only is True by default. To write, add a create method, see: https://www.django-rest-framework.org/api-guide/relations/
    cat = CatRelatedField(read_only=True)
    answers = serializers.HyperlinkedRelatedField(
        view_name='quiz_app:answer_detail', many=True, read_only=True)
    # answers = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id',  'question_text', 'cat', 'answers']
        # extra_kwargs = {'answer': {'required': False} }


class QuestionWriteSerializer(serializers.ModelSerializer):
    cat = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    answers = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=False)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'cat', 'answers']
        # extra_kwargs = {'answer': {'required': False} }


class QuestionPatchSerializer(serializers.ModelSerializer):
    cat = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    answers = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=False)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'answers', 'cat']
        # extra_kwargs = {'answer': {'required': False} }


class AnswerReadSerializer(serializers.ModelSerializer):
    # read only is true by default anyway
    question = QuestionRelatedField(read_only=True)

    class Meta:
        model = Answer
        fields = ['id', 'answer_text', 'correct', 'question']


class AnswerWriteSerializer(serializers.ModelSerializer):
    question = PrimaryKeyRelatedField(queryset=Question.objects.all())

    class Meta:
        model = Answer
        fields = ['id', 'question', 'answer_text', 'correct']


class AnswerPatchSerializer(serializers.ModelSerializer):
    question = PrimaryKeyRelatedField(
        queryset=Question.objects.all(), required=False)

    class Meta:
        model = Answer
        fields = ['id', 'question', 'answer_text', 'correct']
