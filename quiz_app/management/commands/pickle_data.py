from django.conf import settings
from django.core.checks.messages import Error
from django.core.management import BaseCommand, CommandError
from quiz_app.models import Category, UserPoints, Question, Answer
import pickle


class Command(BaseCommand):
    help = 'pickle categories, questions, answers  to store on disk'
    def add_arguments(self, parser):
        pass
    
    def handle(self, *arg, **options):
        ## get all cats, questions, answers objects and pickle them
        cats = Category.objects.all()
        questions = Question.objects.all()
        answers = Answer.objects.all()

        try:
            with open(settings.BASE_DIR / "raw/database/data.pickle", "wb") as f:
                pickle.dump([cats,questions,answers], f)
        except Exception as e:
            raise CommandError("Error pickling the database.", e)
        
        self.stdout.write(self.style.SUCCESS("successfully pickled the database."))
