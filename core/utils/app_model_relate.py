from typing import Dict, List, Optional
from django.apps import apps, AppConfig
from django.conf import settings
from django.db import models


class ModelInspector:
    """
    Django app & model inspection utilities.
    Zero DB hits, safe for production use.
    """

    # -------------------------
    # App-level methods
    # -------------------------
    def get_all_apps(self, app_labels: List[str] = None) -> List[AppConfig]:
        """
        Return all installed apps. If app_labels are provided, return only the apps with the given labels.
        """
        if app_labels:
            return [app for app in apps.get_app_configs() if app.label in app_labels]
        else:
            return list(apps.get_app_configs())


    # -------------------------
    # Model-level methods
    # -------------------------
    def get_models(self, apps: List[AppConfig] = None, model_names: List[str] = None) -> List[models.Model]:
        """
        Return all models in the given app.
        """
        if apps:
            if model_names:
                return [model for app in apps for model in app.get_models() if model.__name__ in model_names]
            else:
                return [model for app in apps for model in app.get_models()]
        elif model_names:
            return [model for model in models.get_models() if model.__name__ in model_names]
        else:
            return list(models.get_models())

    
    def get_model_fields(self, models: models.Model, field_names: List[str] = None) -> List[models.Field]:
        """
        Return all fields in the given model.
        """
        if field_names:
            return [field for field in models._meta.get_fields() if not field.is_relation and field.name in field_names]
        else:
            return [field for field in models._meta.get_fields() if not field.is_relation]