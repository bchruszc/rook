from django import forms
from django.core.exceptions import ValidationError
import datetime
from rookscore.models import Player

def validate_mod5(value):
    if value % 5 != 0:
        raise ValidationError('%s is not a legal rook score' % value)

# I'm sure there is a more elegant solution, but this will get the job done!
class PlayerForm(forms.Form):
    game_date = forms.DateField(initial=datetime.date.today)

    name1 = forms.ModelChoiceField(queryset=Player.objects.all().order_by('first_name'))
    score1 = forms.IntegerField(validators=[validate_mod5])
    star1 = forms.BooleanField(required=False)
    
    name2 = forms.ModelChoiceField(queryset=Player.objects.all().order_by('first_name'))
    score2 = forms.IntegerField(validators=[validate_mod5])
    star2 = forms.BooleanField(required=False)
    
    name3 = forms.ModelChoiceField(queryset=Player.objects.all().order_by('first_name'))
    score3 = forms.IntegerField(validators=[validate_mod5])
    star3 = forms.BooleanField(required=False)
    
    name4 = forms.ModelChoiceField(queryset=Player.objects.all().order_by('first_name'))
    score4 = forms.IntegerField(validators=[validate_mod5])
    star4 = forms.BooleanField(required=False)
    
    name5 = forms.ModelChoiceField(queryset=Player.objects.all().order_by('first_name'), required=False)
    score5 = forms.IntegerField(required=False)
    star5 = forms.BooleanField(required=False)
    
    name6 = forms.ModelChoiceField(queryset=Player.objects.all().order_by('first_name'), required=False)
    score6 = forms.IntegerField(required=False)
    star6 = forms.BooleanField(required=False)
