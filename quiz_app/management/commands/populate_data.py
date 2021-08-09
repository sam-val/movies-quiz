from django.conf import settings
from django.core.checks.messages import Error
from django.core.management import BaseCommand, CommandError
from quiz_app.models import Category, UserPoints, Question, Answer
import pickle


class Command(BaseCommand):
    help = 'Unpickle the raw nessary app data (cats, questions, answers) and populate it into the database. Call on an empty database'
    def add_arguments(self, parser):
        pass
    
    def handle(self, *arg, **options):
        ## get all cats, questions, answers objects and pickle them
        # cats = Category.objects.all()
        # questions = Question.objects.all()
        # answers = Answer.objects.all()

        try:
            with open(settings.BASE_DIR / "raw/database/data.pickle", "rb") as f:
                data = pickle.load(f)
                for queryset in data:
                    model = None
                    if queryset.model == Category:
                        model = Category
                    elif queryset.model == Question:
                        model = Question
                    elif queryset.model == Answer:
                        model = Answer
                    if model == None:
                        raise Exception("model is None")
                    for object in queryset:
                        object_dict = object.__dict__
                        for key in list(object_dict.keys()):
                            if key.startswith('_') or (model == Question and key == "cat_id") or (model == Answer and key == "question_id"):
                                object_dict.pop(key)

                        object_dict.pop('id')
                        model.objects.create(**object_dict)

        except Exception as e:
            raise CommandError("Error unpickling the database.", e)
        
        self.stdout.write(self.style.SUCCESS("successfully unpickled the database."))
