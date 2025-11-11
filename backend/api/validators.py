from django.core.validators import RegexValidator


tag_validator = RegexValidator(
    regex=r'^[-a-zA-Z0-9_]+$',
    message='Тег не соответсвует формату!',
)
