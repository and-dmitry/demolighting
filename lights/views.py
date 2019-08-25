from django.shortcuts import redirect
from django.views.generic import DetailView, ListView

from .models import Lamp


def root_view(request):
    return redirect('lights:lamp-site-list')


class LampListView(ListView):

    model = Lamp


class LampDetailView(DetailView):

    model = Lamp
