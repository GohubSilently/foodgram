from datetime import datetime

from django.template import Engine, Context


MONTHS = {
    1: "Января",
    2: "Февраля",
    3: "Марта",
    4: "Апреля",
    5: "Мая",
    6: "Июня",
    7: "Июля",
    8: "Августа",
    9: "Сентября",
    10: "Октября",
    11: "Ноября",
    12: "Декабря",
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
