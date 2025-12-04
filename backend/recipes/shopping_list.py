from datetime import datetime

from django.template import Engine, Context


MONTHS = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря",
}

now = datetime.now()


def render_shopping_list(user, ingredients, recipes):
    template_str = """
Дата: {{ date }}

Список продуктов:
{% for item in ingredients %}
{{ forloop.counter }}. {{item.name|capfirst}} — {{item.amount}}({{item.unit}})
{% endfor %}

Рецепты:
{% for recipe in recipes %}
- {{ recipe.name }} (Автор: {{ recipe.author.username }})
{% endfor %}
"""

    template = Engine().from_string(template_str)
    return template.render(Context({
        "date": f"{now.day} {MONTHS[now.month]} {now.year}",
        "ingredients": ingredients,
        "recipes": recipes,
        "user": user,
    }))
