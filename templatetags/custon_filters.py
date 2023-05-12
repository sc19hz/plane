from django import template
import json

register = template.Library()

@register.filter
def parse_json(json_string):
    return json.loads(json_string)
