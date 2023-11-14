import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для загрузки данных из CSV-файлов."""

    help = "Загрузка данных из CSV-файлов"

    def create_ingredient(self, model, row):
        """Создание ингредиента на основе данных из строки CSV."""
        model.objects.create(name=row[0], measurement_unit=row[1])

    def handle(self, *args, **kwargs):
        """Обработчик команды для выполнения загрузки данных."""
        if Ingredient.objects.exists():
            self.stdout.write(
                self.style.SUCCESS(
                    "Данные уже существуют, загрузка невозможна."
                )
            )
            return

        with open("data/ingredients.csv", encoding="utf8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.create_ingredient(Ingredient, row)

        self.stdout.write(
            self.style.SUCCESS("Импорт данных завершился успешно!")
        )
