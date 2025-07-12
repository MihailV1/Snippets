from django import template
from MainApp.models import LANG_ICON

register = template.Library()

def get_class_icon(value):
    return LANG_ICON.get(value)


#{{lang | get_class_icon}}

register.filter("get_class_icon", get_class_icon)