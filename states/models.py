from django.db import models

#  STATE MODELS
class State(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    short_description = models.TextField()
    description = models.TextField()

    capital = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)

    image = models.ImageField(
        upload_to='states/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'State'
        verbose_name_plural = 'States'

    def __str__(self):
        return self.name


#HERITAGE PLACE
class HeritagePlace(models.Model):
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name='heritage_places'
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField()

    short_description = models.TextField()
    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to='heritage_places/',
        blank=True,
        null=True
    )

    city = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ['state', 'slug']

    def __str__(self):
        return self.name

# FESTIVALS
class Festival(models.Model):
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name='festivals'
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField()

    short_description = models.TextField()
    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to='festivals/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ['state', 'slug']

    def __str__(self):
        return self.name

# ARTCRAFT
class ArtCraft(models.Model):
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name='arts_crafts'
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField()

    short_description = models.TextField()
    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to='arts_crafts/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ['state', 'slug']

    def __str__(self):
        return self.name

# FOOD
class Food(models.Model):
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name='foods'
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField()

    short_description = models.TextField()
    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to='foods/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ['state', 'slug']

    def __str__(self):
        return self.name

# HISTORICAL EVENTS
class HistoricalEvent(models.Model):
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name='historical_events'
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField()

    short_description = models.TextField()
    description = models.TextField(blank=True)

    year = models.CharField(
        max_length=100,
        blank=True
    )

    location = models.CharField(
        max_length=200,
        blank=True
    )

    image = models.ImageField(
        upload_to='historical_events/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['year', 'title']
        unique_together = ['state', 'slug']

    def __str__(self):
        return self.title


