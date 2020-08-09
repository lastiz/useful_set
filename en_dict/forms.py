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

    def clean(self):
        super().clean()
        word = self.cleaned_data['word']
        user_id = self.cleaned_data['user_id']
        #errors = {}
        user = AdvUser.objects.get(pk=user_id)

        if word and user.words.filter(word=word).values('word'):  # если слово уже есть у пользователя
            raise ValidationError('Данное слово уже есть в вашем словаре!', code='invalid_word')
    
    def save(self, commit=True):
        """Сохраняем слово, если его еще нет в базе и добавляем хозяина"""
        en_word = self.cleaned_data['word']
        user_id = self.cleaned_data['user_id']

        try:
            word_obj = Word.objects.get(word__iexact=en_word)
        except ObjectDoesNotExist:
            word_obj = None  # слова в базе нет

        if en_word and word_obj:  # слово в базе
            word_obj.users.add(user_id)
        elif en_word and not word_obj:  # слова в базе нет, создаем слово и добавляем владельца
            word_obj = super().save()
            word_obj.users.add(user_id)

        if commit:
            word_obj.save()
            #word_obj.save_m2m()
        return word_obj


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
