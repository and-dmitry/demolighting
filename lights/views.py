from django import forms
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView

from django.views.generic.edit import FormView
from django.views.generic.detail import SingleObjectMixin

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


class LampControlView(SingleObjectMixin, FormView):

    model = Lamp
    form_class = LampControlForm
    template_name = 'lights/lamp_control.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_initial(self):
        return {
            'brightness': self.object.brightness,
            'status': (LampControlForm.STATUS_ON if self.object.is_on
                       else LampControlForm.STATUS_OFF)}

    def form_valid(self, form):
        lamp = self.object
        lamp_service.set_lamp_mode(
            lamp,
            on=form.cleaned_data['status'] == form.STATUS_ON,
            brightness=form.cleaned_data['brightness'])
        return super().form_valid(form)
