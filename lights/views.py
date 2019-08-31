from django import forms
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView, UpdateView

from .models import Lamp


def root_view(request):
    return redirect('lights:lamp-site-list')


class LampListView(ListView):

    model = Lamp


class LampDetailView(DetailView):

    model = Lamp


class LampControlForm(forms.ModelForm):
    # Using radio button instead of model's is_on
    STATUS_ON = 'on'
    STATUS_OFF = 'off'
    STATUS_CHOICES = [(STATUS_ON, 'On'),
                      (STATUS_OFF, 'Off')]
    status = forms.ChoiceField(choices=STATUS_CHOICES,
                               widget=forms.RadioSelect)

    class Meta:
        model = Lamp
        fields = ['brightness']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['status'].initial = (
                self.STATUS_ON if self.instance.is_on else self.STATUS_OFF)

    def save(self, commit=True):
        self.instance.is_on = self.cleaned_data['status'] == self.STATUS_ON
        return super().save(commit=commit)


class LampControlView(UpdateView):

    model = Lamp
    template_name = 'lights/lamp_control.html'
    form_class = LampControlForm
