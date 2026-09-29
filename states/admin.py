from django.contrib import admin

from .models import (
    State,
    HeritagePlace,
    Festival,
    ArtCraft,
    Food,
    HistoricalEvent,
)


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'capital',
        'region',
        'created_at',
    )

    search_fields = (
        'name',
        'short_description',
        'description',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }


@admin.register(HeritagePlace)
class HeritagePlaceAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'state',
        'city',
        'created_at',
    )

    list_filter = ('state',)

    search_fields = (
        'name',
        'state__name',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }


@admin.register(Festival)
class FestivalAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'state',
        'created_at',
    )

    list_filter = ('state',)

    search_fields = (
        'name',
        'state__name',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }


@admin.register(ArtCraft)
class ArtCraftAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'state',
        'created_at',
    )

    list_filter = ('state',)

    search_fields = (
        'name',
        'state__name',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'state',
        'created_at',
    )

    list_filter = ('state',)

    search_fields = (
        'name',
        'state__name',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }


@admin.register(HistoricalEvent)
class HistoricalEventAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'state',
        'year',
        'location',
        'created_at',
    )

    list_filter = ('state',)

    search_fields = (
        'title',
        'state__name',
        'location',
    )

    prepopulated_fields = {
        'slug': ('title',)
    }
