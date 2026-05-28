from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import TeacherProfile

@receiver(post_save, sender=User)
def create_teacher_profile(sender, instance, created, **kwargs):
    if created:
        return  # only handle existing users

    # If user is in Teachers group but has no profile → create it
    try:
        teachers_group = Group.objects.get(name='Teachers')
        if teachers_group in instance.groups.all():
            TeacherProfile.objects.get_or_create(
                user=instance,
                defaults={
                    'full_name': instance.get_full_name() or instance.username,
                    'description': ''
                }
            )
    except Group.DoesNotExist:
        pass
