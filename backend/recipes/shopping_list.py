from datetime import datetime

from django.template import Engine, Context


def render_shopping_list(user, ingredients, recipes):
    template_str = """
Дата: {{ date }}

Список продуктов:
{% for item in ingredients %}
{{ forloop.counter }}. {{item.name|capfirst}} — {{item.amount}}{{item.unit}}
{% endfor %}

Рецепты:
{% for recipe in recipes %}
- {{ recipe.name }} (Автор: {{ recipe.author.username }})
{% endfor %}
"""

    template = Engine().from_string(template_str)
    return template.render(Context({
        "date": datetime.now().strftime("%d %B %Y"),
        "ingredients": ingredients,
        "recipes": recipes,
        "user": user,
    }))
