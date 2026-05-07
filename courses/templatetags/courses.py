import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def model_name(obj):
    try:
        return obj._meta.model_name
    except AttributeError:
        return None
    
@register.filter(name="markdown")
def markdown_filter(text):
    return mark_safe(markdown.markdown(text))

@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()