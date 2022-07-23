from django import forms


class MazeForm(forms.Form):
    height = forms.IntegerField(min_value=4)
    width = forms.IntegerField(min_value=4)
