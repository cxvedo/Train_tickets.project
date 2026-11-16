from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking, Passenger


# მატარებლების საძიებო ფორმა (მთავარი გვერდისთვის)
class TrainSearchForm(forms.Form):
    # გამგზავრების სადგურის ველი (არასავალდებულო, Bootstrap-ის სტილითა და placeholder-ით)
    origin = forms.CharField(
        required=False, 
        label="საიდან", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'საიდან'})
    )
    # დანიშნულების სადგურის ველი (არასავალდებულო)
    destination = forms.CharField(
        required=False, 
        label="სად", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'სად'})
    )
    # გამგზავრების თარიღის ველი (type='date' ბრაუზერში აჩენს სტანდარტულ კალენდარს)
    date = forms.DateField(
        required=False, 
        label="თარიღი", 
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )


# მომხმარებლის რეგისტრაციის გაფართოებული ფორმა (მემკვიდრეობით იღებს სტანდარტულ UserCreationForm-ს)
class RegisterForm(UserCreationForm):
    # სტანდარტულ ფორმას ემატება ელ-ფოსტის სავალდებულო ველი
    email = forms.EmailField(
        required=True, 
        label="ელ-ფოსტა", 
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ელ-ფოსტა'})
    )

    # ფორმის მეტა-მონაცემები: რომელ მოდელთან მუშაობს და რომელი ველები გამოჩნდეს (პაროლის ველებს UserCreationForm ავტომატურად ამატებს)
    class Meta:
        model = User
        fields = ['username', 'email']