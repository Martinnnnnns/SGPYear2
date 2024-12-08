from django import template

register = template.Library()

# Custom filter to get a field dynamically from an object
@register.filter
def get_item(obj, field_name):
    return getattr(obj, field_name, None)
