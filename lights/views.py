from django import forms
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView, View

from .models import Lamp
from .services import lamp_service


def root_view(request):
    return redirect('lights:lamp-site-list')


class LampListView(ListView):

    model = Lamp


class LampDetailView(DetailView):

    model = Lamp


# Simple Form seems like a better fit here than ModelForm. We're
# changing one field, providing min and max values to the widget for
# the other. And we don't need save().
class LampControlForm(forms.Form):
    # Using radio button instead of model's is_on
    STATUS_ON = 'on'
    STATUS_OFF = 'off'
    STATUS_CHOICES = [(STATUS_ON, 'On'),
                      (STATUS_OFF, 'Off')]
    status = forms.ChoiceField(choices=STATUS_CHOICES,
                               widget=forms.RadioSelect)

    # Can't use formfield() to copy field from model, because it
    # ignores min and max validators.
    brightness = forms.IntegerField(
        label='Brightness %',
        min_value=1,
        max_value=100)


class LampControlView(View):

    def get(self, request, pk):
        lamp = get_object_or_404(Lamp, pk=pk)
        status = (LampControlForm.STATUS_ON if lamp.is_on
                  else LampControlForm.STATUS_OFF)
        form = LampControlForm(initial={
            'brightness': lamp.brightness,
            'status': status})
        return render(request, 'lights/lamp_control.html', {
            'lamp': lamp,
            'form': form,
        })

    def post(self, request, pk):
        lamp = get_object_or_404(Lamp, pk=pk)
        form = LampControlForm(request.POST)
        if form.is_valid():
            lamp_service.set_lamp_mode(
                lamp,
                on=form.cleaned_data['status'] == form.STATUS_ON,
                brightness=form.cleaned_data['brightness'])
            return redirect(lamp)

        return render(request, 'lights/lamp_control.html', {
            'lamp': lamp,
            'form': form,
        })
