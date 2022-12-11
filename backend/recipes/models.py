from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Теги рецептов.
        Связана с моделью Recipe через М2М.
    """

    name = models.CharField(
        verbose_name='Тег',
        max_length=150,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цветовой HEX-код',
        max_length=6,
        blank=True,
        null=True,
        default='FF',
    )
    slug = models.SlugField(
        verbose_name='Слаг тэга',
        max_length=150,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name', )

    def __str__(self):
        return f'{self.name}, (цвет: {self.color})'


class Ingredient(models.Model):
    """Ингредиенты рецептов.
        Связана с моделью Recipe через М2М
        при помощи посреднической модели AmountIngredient
    """

    name = models.CharField(
        verbose_name='Ингридиент',
        max_length=150,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=150,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    """Рецепты.
    Attributes:
        name(str):
        author(int):
            Автор рецепта. Связан с моделю User через ForeignKey.
        favorite(int):
            Связь M2M с моделью User.
            Создаётся при добавлении пользователем рецепта в `избранное`.
        tags(int):
            Связь M2M с моделью Tag.
        ingredients(int):
            Связь M2M с моделью Ingredient. Связь создаётся посредством модели
            AmountIngredient с указанием количества ингридиента.
        cart(int):
            Связь M2M с моделью User.
            Создаётся при добавлении пользователем рецепта в `покупки`.
        pub_date(datetime):
        image(str):
            Изображение рецепта. Указывает путь к изображению.
        text(str):
        cooking_time(int):
    """

    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    favorite = models.ManyToManyField(
        User,
        verbose_name='Понравившееся рецепты',
        related_name='favorites',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги рецепта',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты блюда',
        related_name='recipes',
        through='recipes.AmountIngredient',
    )
    cart = models.ManyToManyField(
        User,
        verbose_name='Список покупок',
        related_name='carts',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления рецепта',
        auto_now_add=True,
    )
    image = models.ImageField(
        verbose_name='Картинка блюда',
        upload_to='recipes.images/%Y/%m/%d/'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления, минут'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )

    def __str__(self):
        return f'{self.name}. Автор: {self.author}'


class AmountIngredient(models.Model):
    """Количество ингредиентов в блюде.
        Связывает Recipe и Ingredient,
        добавляет количество ингредиента для конкретного рецепта.
    """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='В каких рецептах',
        related_name='ingredient',
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='Связанные ингредиенты',
        related_name='recipe',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=0,
        validators=(
            MinValueValidator(1, 'Нужно хоть какое-то количество.'),
            MaxValueValidator(10000, 'Слишком много!'),
        ),
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'
        ordering = ('recipe', )

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredients}'
