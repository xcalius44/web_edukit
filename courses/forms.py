from django.forms.models import inlineformset_factory
from .models import Course, Lesson

LessonFormSet = inlineformset_factory(
    Course,
    Lesson,
    fields=['title', 'description'],
    extra=1,
    can_delete=True
)
