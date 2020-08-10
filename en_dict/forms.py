from django import forms
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from .models import Word
from users.models import AdvUser


class WordAddForm(forms.ModelForm):
    """Форма для добавление слова"""
    user_id = forms.IntegerField(widget=forms.HiddenInput())  # для объявления текущего пользователя во вьюхе

    class Meta:
        model = Word
        fields = ('word', 'transfer', )
        widgets = {
            'word': forms.TextInput(attrs={
                'placeholder': 'Введите слово',
                'pattern': r'[a-zA-Z]+',
                'title': 'Только символы английского алфавита',
                'autofocus': 'autofocus',
            }),
            'transfer': forms.TextInput(attrs={
                'placeholder': 'Введите перевод',
                'pattern': r'[а-яА-Я]+',
                'title': 'Только символы русского алфавита',
            }),
        }
        labels = {'word': 'Cлово', 'transfer': 'Перевод', }
        help_texts = {
            'word': 'Введите слово на английском языке (разрешены только символы анлийского алфавита)',
            'transfer': 'Введите перевод на русском языке (разрешены только символы русского алфавита)',
        }

    def clean_word(self):
        return self.cleaned_data.get('word').lower()
                                                            # преобразование всех полей в нижний регистр
    def clean_transfer(self):
        return self.cleaned_data.get('transfer').lower()
        

    def clean(self):
        super().clean()
        word = self.cleaned_data['word']
        transfer = self.cleaned_data['transfer']
        user_id = self.cleaned_data['user_id']
        #errors = {}
        self.user = AdvUser.objects.get(pk=user_id)

        if word and self.user.words.filter(word__iexact=word).exists():  # если слово уже есть у пользователя
            raise ValidationError('Данное слово уже есть в вашем словаре!', code='invalid_word')
        
        # проверка на наличие введенного перевода у пользователя в словаре
        check_transfer = self.user.words.values('word', 'transfer').filter(transfer__iexact=transfer)
        if transfer and check_transfer:
            raise ValidationError(f'Данный перевод уже есть в вашем словаре! ({check_transfer[0].get("transfer")} < --- > {check_transfer[0].get("word")})',
                                                                                                                        code='invalid_transfer')
    
    def save(self, commit=True):
        """Сохраняем слово, если его еще нет в базе и добавляем хозяина"""
        word = super().save(commit=False)
        word.owner = self.user

        if commit:
            word.save()
        return word


class WordEnterForm(forms.Form):
    """Форма для тренировки"""
    def __init__(self, *args, **kwargs):
        self.word = kwargs.pop('word')
        self.help_text = 'Введите перевод на русский' if self.word[1] == 'en' else 'Введите перевод на английский'
        self.pattern = r'[а-яА-Я]+' if self.word[1] == 'en' else r'[a-zA-Z]+'
        super().__init__(*args, **kwargs)
        self.fields['transfer'].widget = forms.TextInput(attrs={
            'autofocus': 'autofocus',
            'placeholder': 'Введите перевод',
            'pattern': self.pattern,
            'title': 'Введите перевод на русский' if self.word[1] == 'en' else 'Введите перевод на английский',
        })
        self.fields['transfer'].help_text = self.help_text
        self.fields['language'].initial = self.word[1]

    transfer = forms.CharField(max_length=30, label='Перевод')
    language = forms.CharField(max_length=2, widget=forms.HiddenInput())
