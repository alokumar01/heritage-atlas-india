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
        'updated_at',
    )

    list_filter = (
        'region',
    )

    search_fields = (
        'name',
        'capital',
        'region',
        'short_description',
        'description',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }

    ordering = (
        'name',
    )

    list_per_page = 20


@admin.register(HeritagePlace)
class HeritagePlaceAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'state',
        'city',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'state',
        'city',
    )

    search_fields = (
        'name',
        'state__name',
        'city',
        'short_description',
        'description',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }

    ordering = (
        'state',
        'name',
    )

    list_per_page = 20


@admin.register(Festival)
class FestivalAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'state',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'state',
    )

    search_fields = (
        'name',
        'state__name',
        'short_description',
        'description',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }

    ordering = (
        'state',
        'name',
    )

    list_per_page = 20


@admin.register(ArtCraft)
class ArtCraftAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'state',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'state',
    )

    search_fields = (
        'name',
        'state__name',
        'short_description',
        'description',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }

    ordering = (
        'state',
        'name',
    )

    list_per_page = 20


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'state',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'state',
    )

    search_fields = (
        'name',
        'state__name',
        'short_description',
        'description',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }

    ordering = (
        'state',
        'name',
    )

    list_per_page = 20  


@admin.register(HistoricalEvent)
class HistoricalEventAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'state',
        'year',
        'location',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'state',
        'year',
    )

    search_fields = (
        'title',
        'state__name',
        'year',
        'location',
        'short_description',
        'description',
    )

    prepopulated_fields = {
        'slug': ('title',)
    }

    ordering = (
        'state',
        'year',
        'title',
    )

    list_per_page = 20
