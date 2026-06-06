from django.apps import AppConfig


class RatingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ratings"
    verbose_name = 'Ratings and Comments'
