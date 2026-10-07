from django.shortcuts import render

from states.models import State


def home(request):
    states = State.objects.all()

    query = request.GET.get('q', '').strip()

    if query:
        states = states.filter(name__icontains=query)

    context = {
        'states': states,
        'query': query,
    }

    return render(request, 'core/home.html', context)


def explore(request):
    states = State.objects.all()

    query = request.GET.get('q', '').strip()
    region = request.GET.get('region', '').strip()

    if query:
        states = states.filter(name__icontains=query)

    if region:
        states = states.filter(region=region)

    regions = (
        State.objects
        .exclude(region='')
        .values_list('region', flat=True)
        .order_by()
        .distinct()
    )

    context = {
        'states': states,
        'query': query,
        'region': region,
        'regions': regions,
    }

    return render(request, 'core/explore.html', context)


def about(request):
    return render(request, 'core/about.html')
