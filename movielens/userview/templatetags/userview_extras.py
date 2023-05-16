from django import template
from ..models import Rating

register = template.Library()

@register.filter
def rating_value(movie, user):
    try:
        rating = movie.rating_set.get(user=user)
        return rating.value
    except Rating.DoesNotExist:
        return None