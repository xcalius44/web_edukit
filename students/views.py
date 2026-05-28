from multiprocessing import context

from django.contrib.auth.models import Group
from .forms import CourseEnrollForm, StudentRegistrationForm, TeacherRegistrationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404, redirect

from .models import TeacherProfile
from .forms import CourseEnrollForm
from courses.models import Course
from .forms import TeacherProfileUpdateForm

class StudentRegistrationView(CreateView):
    template_name = 'students/register.html'
    form_class = StudentRegistrationForm
    success_url = reverse_lazy('student_course_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role'] = 'student'
        return context

    def form_valid(self, form):
        user = form.save()
        group = Group.objects.get(name='Students')
        group.user_set.add(user)
        login(self.request, user)
        return redirect(self.success_url)


class TeacherRegistrationView(CreateView):
    template_name = 'students/register.html'
    form_class = TeacherRegistrationForm
    success_url = reverse_lazy('manage_course_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role'] = 'teacher'
        return context

    def form_valid(self, form):
        user = form.save()

        # Create teacher profile
        TeacherProfile.objects.create(
            user=user,
            full_name=form.cleaned_data['full_name'],
            description=form.cleaned_data['description'],
            youtube=form.cleaned_data['youtube'],
            telegram=form.cleaned_data['telegram'],
            linkedin=form.cleaned_data['linkedin'],
            website=form.cleaned_data['website']
        )


        # Assign group
        group = Group.objects.get(name='Teachers')
        group.user_set.add(user)

        login(self.request, user)
        return redirect(self.success_url)

    

class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        if not self.course.students.filter(id=self.request.user.id).exists():
            self.course.students.add(self.request.user)
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('student_course_detail', args=[self.course.id])

class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])

class StudentCourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'students/course/detail.html'
    context_object_name = 'course'

    def get_queryset(self):
        return Course.objects.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()

        lessons = course.lessons.all()
        context['lessons'] = lessons

        # ⭐ If ?lesson=ID → show that lesson
        lesson_id = self.request.GET.get("lesson")
        if lesson_id:
            context['selected_lesson'] = lessons.filter(id=lesson_id).first()
        else:
            # ⭐ No lesson selected → show course description
            context['selected_lesson'] = None

        return context


    
class TeacherProfileView(DetailView):
    model = TeacherProfile
    template_name = 'students/teacher/profile.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()

        # All courses created by this teacher
        courses = Course.objects.filter(owner=profile.user)
        context['courses'] = courses

        # Selected course
        course_id = self.request.GET.get("course")
        if course_id:
            selected_course = Course.objects.filter(id=course_id, owner=profile.user).first()
        else:
            selected_course = courses.first()

        context['selected_course'] = selected_course

        # Lessons of selected course
        if selected_course:
            lessons = selected_course.lessons.all()
            context['lessons'] = lessons

            # Selected lesson
            lesson_id = self.request.GET.get("lesson")
            if lesson_id:
                selected_lesson = lessons.filter(id=lesson_id).first()
            else:
                selected_lesson = lessons.first()

            context['selected_lesson'] = selected_lesson

        return context

class TeacherProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = TeacherProfile
    form_class = TeacherProfileUpdateForm
    template_name = 'students/teacher/profile_edit.html'
    context_object_name = 'profile'

    def test_func(self):
        # Only allow the owner of the profile to edit it
        return self.get_object().user == self.request.user

    def get_success_url(self):
        return reverse_lazy('teacher_profile', args=[self.object.id])
