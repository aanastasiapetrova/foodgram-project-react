from typing import Any

import pandas as pd
from django.core.management.base import BaseCommand, CommandParser

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'importing data from csv'

    def add_arguments(self, parser: CommandParser) -> None:
        pass

    def handle(self, *args: Any, **options: Any) -> str | None:
        df = pd.read_csv('../data/ingredients.csv')
        for import_name, import_measurement_unit in zip(
            df.iloc[:, 0], df.iloc[:, 1]
        ):
            models = Ingredient(
                name=import_name,
                measurement_unit=import_measurement_unit
                                )
            models.save()
