from django import forms


class MazeForm(forms.Form):
    height = forms.IntegerField(min_value=4, max_value=33)
    width = forms.IntegerField(min_value=4, max_value=33)
