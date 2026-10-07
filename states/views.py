from django.shortcuts import get_object_or_404, render

from .models import State


def state_detail(request, slug):
    state = get_object_or_404(State, slug=slug)

    states = State.objects.all()

    previous_state = (
        states
        .filter(name__lt=state.name)
        .order_by('-name')
        .first()
    )

    next_state = (
        states
        .filter(name__gt=state.name)
        .order_by('name')
        .first()
    )

    context = {
        'state': state,
        'heritage_places': state.heritage_places.all(),
        'festivals': state.festivals.all(),
        'arts_crafts': state.arts_crafts.all(),
        'foods': state.foods.all(),
        'historical_events': state.historical_events.all(),
        'previous_state': previous_state,
        'next_state': next_state,
    }

    return render(
        request,
        'states/state_detail.html',
        context
    )
