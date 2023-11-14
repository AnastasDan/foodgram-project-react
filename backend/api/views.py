from django.db.models import Sum
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import BaseFilterBackend
from rest_framework.pagination import BasePagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag
)
from users.models import MyUser, Subscribe

from .filters import IngredientFilter, RecipeFilter
from .permissions import OwnerOnlyPermission
from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeGETSerializer,
    ShoppingListSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserGETSerializer
)
from .utils import add_or_remove_favorite_and_shopping_list


class MeView(APIView):
    """Представление для получения данных о текущем пользователе."""

    permission_classes: tuple[type[IsAuthenticated]] = (IsAuthenticated,)

    def get(self, request, *args, **kwargs) -> Response:
        """Получение данных о текущем пользователе."""
        serializer: type[UserGETSerializer] = UserGETSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscribeView(APIView):
    """Представление для подписки и отписки от авторов."""

    permission_classes: tuple[type[IsAuthenticated]] = (IsAuthenticated,)

    def get_user_author(self, request, pk: int) -> tuple[MyUser, MyUser]:
        """Получение текущего пользователя и автора по идентификатору."""
        user: MyUser = request.user
        author: MyUser = get_object_or_404(MyUser, id=pk)
        return user, author

    def check_subscription_exists(self, user: MyUser, author: MyUser) -> bool:
        """Проверка наличия подписки."""
        return Subscribe.objects.filter(user=user, author=author).exists()

    def post(self, request, pk: int = None) -> Response:
        """Подписка на автора."""
        user, author = self.get_user_author(
            request, pk
        )  # type: tuple[MyUser, MyUser]

        if self.check_subscription_exists(user, author):
            return Response(
                {"ошибка": "вы уже подписаны"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user == author:
            return Response(
                {"ошибка": "нельзя подписываться на самого себя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer: type[SubscriptionSerializer] = SubscriptionSerializer(
            author, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        Subscribe.objects.create(user=user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk: int = None) -> Response:
        """Отписка от автора."""
        user, author = self.get_user_author(
            request, pk
        )  # type: tuple[MyUser, MyUser]

        if not self.check_subscription_exists(user, author):
            return Response(
                {"ошибка": "вы на автора не подписаны"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        get_object_or_404(Subscribe, user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsListView(generics.ListAPIView):
    """Список подписок пользователя."""

    serializer_class: type[SubscriptionSerializer] = SubscriptionSerializer
    permission_classes: tuple[type[IsAuthenticated]] = (IsAuthenticated,)

    def get_queryset(self) -> QuerySet[MyUser]:
        """Получение списка подписок пользователя."""
        user: MyUser = self.request.user
        users: QuerySet[MyUser] = MyUser.objects.filter(following__user=user)
        return self.paginate_queryset(users)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для просмотра тегов."""

    queryset: QuerySet[Tag] = Tag.objects.all()
    serializer_class: type[TagSerializer] = TagSerializer
    permission_classes: tuple[type[AllowAny]] = (AllowAny,)
    pagination_class: type[BasePagination] = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для просмотра ингредиентов."""

    queryset: QuerySet[Ingredient] = Ingredient.objects.all()
    serializer_class: type[IngredientSerializer] = IngredientSerializer
    permission_classes: tuple[type[AllowAny]] = (AllowAny,)
    filter_backends: tuple[type[BaseFilterBackend]] = (DjangoFilterBackend,)
    filterset_class: type[IngredientFilter] = IngredientFilter
    pagination_class: type[BasePagination] = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для просмотра и редактирования рецептов."""

    queryset: QuerySet[Recipe] = Recipe.objects.all()
    permission_classes: tuple[type[OwnerOnlyPermission]] = (
        OwnerOnlyPermission,
    )
    filter_backends: tuple[type[BaseFilterBackend]] = (DjangoFilterBackend,)
    filterset_class: type[RecipeFilter] = RecipeFilter

    def get_serializer_class(self):
        """Определение, какой сериализатор использовать."""
        if self.action in ("list", "retrieve"):
            return RecipeGETSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk: int = None) -> Response:
        """Добавление или удаление рецепта из избранного."""
        user: MyUser = request.user
        return add_or_remove_favorite_and_shopping_list(
            request, user, FavoriteRecipe, FavoriteSerializer, pk
        )

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk: int = None) -> Response:
        """Добавление или удаление рецепта из списка покупок."""
        user: MyUser = request.user
        return add_or_remove_favorite_and_shopping_list(
            request, user, ShoppingList, ShoppingListSerializer, pk
        )

    @action(
        detail=False,
        methods=("get",),
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request) -> HttpResponse:
        """Загрузка списка покупок ингредиентов в виде текстового файла."""
        user: MyUser = request.user
        recipes_in_shopping_list: QuerySet[RecipeIngredient] = (
            RecipeIngredient.objects.filter(
                recipe__in_shopping_lists__user=user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
        )

        shopping_list: list[str] = ["Список покупок:\n"]

        for recipe in recipes_in_shopping_list:
            name: str = recipe["ingredient__name"]
            total_amount: int = recipe["total_amount"]
            measurement_unit: str = recipe["ingredient__measurement_unit"]
            shopping_list.append(
                f"{name} ({measurement_unit}) - {total_amount}\n"
            )

        response: HttpResponse = HttpResponse(
            shopping_list, content_type="text/plain"
        )
        response[
            "Content-Disposition"
        ] = 'attachment; filename="shopping_list.txt"'
        return response
