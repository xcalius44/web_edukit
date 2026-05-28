from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.loader import render_to_string

from .fields import OrderField


from django.contrib.auth.models import User
from django.db import models


class Subject(models.Model):
    title = models.CharField(max_length=200, verbose_name="Назва")
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = "Спеціалізація"
        verbose_name_plural = "Спеціалізації"
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(User, related_name='courses_created', on_delete=models.CASCADE, verbose_name="Викладач")
    subject = models.ForeignKey(Subject, related_name="courses", on_delete=models.CASCADE, verbose_name="Спеціалізація")
    title = models.CharField(max_length=500, verbose_name="Назва")
    slug = models.SlugField(max_length=500, unique=True, verbose_name="Коротка назва")
    overview = models.TextField(verbose_name="Опис")
    created = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(User, related_name='course_joined', blank=True, verbose_name="Зараховані студенти")

    published = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курси"
        ordering = ['-created']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    video = models.URLField(blank=True)
    description = models.TextField(blank=True)
    links = models.TextField(blank=True)
    file = models.FileField(upload_to='lessons/files/', blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Content(models.Model):
    lesson = models.ForeignKey(Lesson, related_name="contents", on_delete=models.CASCADE, verbose_name="Урок")
    title = models.CharField(max_length=200)
    text = models.TextField(blank=True)
    file = models.FileField(upload_to="content/files/", blank=True)
    video = models.URLField(blank=True)
    link = models.URLField(blank=True)

    class Meta:
        verbose_name = "Контент"
        verbose_name_plural = "Контент"
        ordering = ['id']

    def __str__(self):
        return self.title

class BaseContent(models.Model):
    owner = models.ForeignKey(User, related_name="%(class)s_related", on_delete=models.CASCADE, verbose_name="Автор")
    title = models.CharField(max_length=500, verbose_name="Назва")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title
    
    def render(self):
        return render_to_string(
            f'courses/content/{self._meta.model_name}.html',
            {'item': self}
        )

class Text(BaseContent):
    content = models.TextField(verbose_name="Текст")

class File(BaseContent):
    file = models.FileField(upload_to="files", verbose_name="Файл")

class Image(BaseContent):
    file = models.FileField(upload_to="images", verbose_name="Зображення")

class Video(BaseContent):
    url = models.URLField(verbose_name="Відео")

class URL(BaseContent):
    url = models.URLField(verbose_name="Лінк")