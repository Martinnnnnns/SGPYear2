from django import template

register = template.Library()

@register.filter
def has_multiple_roles(user):
    return user.roles.count() > 1
