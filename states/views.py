from django.shortcuts import get_object_or_404, render

from .models import State


def state_detail(request, slug):
    state = get_object_or_404(State, slug=slug)

    context = {
        'state': state,
        'heritage_places': state.heritage_places.all(),
        'festivals': state.festivals.all(),
        'arts_crafts': state.arts_crafts.all(),
        'foods': state.foods.all(),
        'historical_events': state.historical_events.all(),
    }

    return render(
        request,
        'states/state_detail.html',
        context
    )
