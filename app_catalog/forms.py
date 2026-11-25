from django import forms


class AccountForm(forms.Form):
    name = forms.CharField(max_length=100, label='Имя')
    email = forms.EmailField(label='Email')
    phone = forms.CharField(required=False, max_length=20, label='Телефон')

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if not name:
            raise forms.ValidationError('Поле «Имя» обязательно. Введите ваше имя.')
        return name


class BookingForm(forms.Form):
    start_date = forms.DateField(label='Дата начала')
    end_date = forms.DateField(label='Дата возврата')

    def clean(self):
        cleaned = super().clean()
        d1, d2 = cleaned.get('start_date'), cleaned.get('end_date')
        if d1 and d2 and d2 <= d1:
            raise forms.ValidationError('Дата возврата должна быть позже даты начала.')
        return cleaned