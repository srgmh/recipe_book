from django.contrib import admin

from recipes.models import AmountIngredient, Ingredient, Recipe, Tag


class IngredientInline(admin.TabularInline):
    model = AmountIngredient
    min_num = 1
    extra = 2


@admin.register(AmountIngredient)
class LinksAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', )
    search_fields = ('name', )
    list_filter = ('name', )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', )
    fields = (
        ('name', 'cooking_time',),
        ('author', 'tags',),
        ('text',),
        ('image',),
    )
    search_fields = ('name', 'author', )
    list_filter = ('name', 'author__username', )
    inlines = (IngredientInline,)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug', )
    search_fields = ('name', 'color', )
