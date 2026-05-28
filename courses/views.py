from multiprocessing import context

from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.apps import apps
from django.db.models import Count
from django.forms.models import modelform_factory
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


from django.db.models import Count, Q
from django.views import View
from urllib3 import request
from .mixins import OwnerCourseEditMixin, OwnerCourseMixin, OwnerEditMixin
from .models import Course, Content, Lesson, Lesson, Subject
from students.forms import CourseEnrollForm


class HomeView(TemplateView):
    template_name = "base.html"


class ManageCourseListView(OwnerCourseMixin, ListView):
    model = Course
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'

    def get_queryset(self):
        # Only courses owned by the teacher
        return Course.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()

        context['my_courses'] = qs
        context['published_courses'] = qs.filter(published=True)
        context['unpublished_courses'] = qs.filter(published=False)
        context['enrolled_courses'] = Course.objects.filter(students__in=[self.request.user])

        return context

class CourseCreateView(OwnerEditMixin, OwnerCourseMixin, CreateView):
    permission_required = 'courses.add_course'
    template_name = 'courses/manage/course/form.html'

class CourseUpdateView(OwnerEditMixin, OwnerCourseMixin, UpdateView):
    permission_required = 'courses.change_course'
    template_name = 'courses/manage/course/form.html'

@method_decorator(login_required, name='dispatch')
class CourseStudioView(TemplateResponseMixin, View):
    template_name = "courses/manage/studio.html"

    def dispatch(self, request, course_id, lesson_id=None):
        self.course = get_object_or_404(Course, id=course_id, owner=request.user)
        self.lesson = None
        if lesson_id:
            self.lesson = get_object_or_404(Lesson, id=lesson_id, course=self.course)
        return super().dispatch(request, course_id, lesson_id)

    def get(self, request, *args, **kwargs):
        return self.render_to_response({
            "course": self.course,
            "lessons": self.course.lessons.all(),
            "lesson": self.lesson,
        })

    def post(self, request, course_id, lesson_id=None):
        action = request.POST.get("action")

        # ⭐ CREATE LESSON
        if action == "create_lesson":
            lesson = Lesson.objects.create(
                course=self.course,
                title="Новий урок",
                order=self.course.lessons.count()
            )
            return redirect("course_studio_lesson", self.course.id, lesson.id)
        
        # ⭐ DELETE LESSON
        if action == "delete_lesson" and lesson_id:
            lesson = get_object_or_404(Lesson, id=lesson_id, course=self.course)
            lesson.delete()

            # Reorder remaining lessons
            for index, l in enumerate(self.course.lessons.all()):
                l.order = index
                l.save()

            return redirect("course_studio", self.course.id)


        # ⭐ AUTOSAVE LESSON (no redirect)
        if action == "autosave_lesson":
            lesson = get_object_or_404(Lesson, id=request.POST["lesson_id"], course=self.course)
            lesson.title = request.POST.get("title")
            lesson.video = request.POST.get("video")
            lesson.description = request.POST.get("description")
            lesson.links = request.POST.get("links")
            if request.FILES.get("file"):
                lesson.file = request.FILES["file"]
            lesson.save()
            return JsonResponse({"status": "ok"})

        # ⭐ FINAL SAVE → redirect to My Courses
        if action == "final_save":
            if lesson_id:
                lesson = get_object_or_404(Lesson, id=lesson_id, course=self.course)
                lesson.title = request.POST.get("title")
                lesson.video = request.POST.get("video")
                lesson.description = request.POST.get("description")
                lesson.links = request.POST.get("links")
                if request.FILES.get("file"):
                    lesson.file = request.FILES["file"]
                lesson.save()
            else:
                self.course.title = request.POST.get("title")
                self.course.slug = request.POST.get("slug")
                self.course.overview = request.POST.get("overview")
                self.course.save()

            return redirect("manage_course_list")  # ⭐ redirect to My Courses
        
        if action == "delete_file" and lesson_id:
            lesson = get_object_or_404(Lesson, id=lesson_id, course=self.course)
            lesson.file.delete(save=True)
            return redirect("course_studio_lesson", self.course.id, lesson.id)


        # ⭐ DEFAULT: update course or lesson (fallback)
        if not lesson_id:
            self.course.title = request.POST.get("title")
            self.course.slug = request.POST.get("slug")
            self.course.overview = request.POST.get("overview")
            self.course.save()
            return redirect("course_studio", self.course.id)

        lesson = get_object_or_404(Lesson, id=lesson_id, course=self.course)
        lesson.title = request.POST.get("title")
        lesson.video = request.POST.get("video")
        lesson.description = request.POST.get("description")
        lesson.links = request.POST.get("links")
        if request.FILES.get("file"):
            lesson.file = request.FILES["file"]
        lesson.save()

        return redirect("course_studio_lesson", self.course.id, lesson.id)


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    permission_required = 'courses.delete_course'
    template_name = 'courses/manage/course/delete.html'

class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ('text', 'file', 'video', 'image', 'url'):
            return apps.get_model(app_label='courses', model_name=model_name)
        return None
    
    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=[
            'owner', 'order', 'created', 'updated',
        ])
        return Form(*args, **kwargs)
    
    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Lesson, id=module_id, course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id, owner=request.user)
        return super().dispatch(request, module_id, model_name, id)
    
    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({
            'form': form,
            'object': self.obj,
        })
    
    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                Content.objects.create(module=self.module, item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({
            'form': form,
            'object': self.obj,
        })

class ContentDeleteView(View):

    def post(self, request, id):
        content = get_object_or_404(Content, id=id, module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)

class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'
    content_types = ["text", "image", "file", "url", "video"]

    def get(self, request, module_id):
        module = get_object_or_404(Lesson, id=module_id, course__owner=request.user)
        return self.render_to_response({
            'module': module,
            'content_types': self.content_types,
        })

class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):

    def post(self, request):
        for id, order in self.request_json.items():
            Lesson.objects.filter(
                id=id,
                course__owner=request.user
            ).update(order=order)
        return self.render_json_response({'saved': 'OK'})

class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):

    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(
                id=id,
                module__course__owner=request.user
            ).update(order=order)
        return self.render_json_response({'saved': 'Ok'})

class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        subjects = Subject.objects.annotate(
            total_courses=Count('courses', filter=Q(courses__published=True))
        ).filter(total_courses__gt=0)

        # ⭐ FIXED: replace modules → lessons
        courses = Course.objects.filter(published=True).annotate(
            total_lessons=Count('lessons')
        )

        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            courses = courses.filter(subject=subject, published=True)

        return self.render_to_response({
            'subjects': subjects,
            'subject': subject,
            'courses': courses,
        })

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'
    context_object_name = "course"

    def get(self, request, *args, **kwargs):
        course = self.get_object()

        # ⭐ If user is enrolled → redirect to learning page
        if request.user.is_authenticated:
            if course.students.filter(id=request.user.id).exists():
                return redirect("student_course_detail", course.id)

        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        course = super().get_object(queryset)
        user = self.request.user

        # Owner can always view
        if course.owner == user:
            return course

        # Enrolled students can view (but will be redirected in get())
        if user.is_authenticated and course.students.filter(id=user.id).exists():
            return course

        # Everyone else can view ONLY if published
        if course.published:
            return course

        # Otherwise block access
        raise Http404("This course is not available")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()

        # Enrollment form
        context['enroll_form'] = CourseEnrollForm(initial={'course': course})

        # Teacher profile
        if hasattr(course.owner, "teacher_profile"):
            context['teacher_profile'] = course.owner.teacher_profile
        else:
            context['teacher_profile'] = None

        # More courses by this teacher
        context['more_courses'] = Course.objects.filter(owner=course.owner).exclude(id=course.id)[:5]

        return context




class PublishCourseView(OwnerCourseMixin, View):
    permission_required = 'courses.change_course'

    def post(self, request, pk):
        course = get_object_or_404(Course, id=pk, owner=request.user)
        course.published = True
        course.save()
        return redirect('manage_course_list')


class UnpublishCourseView(OwnerCourseMixin, View):
    permission_required = 'courses.change_course'

    def post(self, request, pk):
        course = get_object_or_404(Course, id=pk, owner=request.user)
        course.published = False
        course.save()
        return redirect('manage_course_list')

class LessonDeleteView(View):
    def post(self, request, course_id, lesson_id):
        course = get_object_or_404(Course, id=course_id, owner=request.user)
        lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
        lesson.delete()
        return redirect('course_studio', course.id)
