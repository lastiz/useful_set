from random import choice
from collections import namedtuple
from .models import Word


def get_random_obj(queryset):
    """Выбирает случайный объект из queryset"""
    return choice(queryset)

def get_percent(val1, val2):
    """Возвращает float с 1 цифрой после запятой"""
    assert val2 != 0, 'Деление на ноль в en_dict.utilites.get_percent'
    return float('{:.1f}'.format(val1 / val2 * 100))


class Training:
    """Объект для тренировки (view training)"""

    def __init__(self, request):
        self.request = request
        self.pk_ans_words = request.session.setdefault('pk_ans_words', [])
        self.true_ans = request.session.setdefault('true_ans', 0)
        self.count_ans = request.session.get('count_ans', 0)

    def check_transfer(self, form):
        """Проверка перевода"""
        transfer = form.cleaned_data['transfer']
        lan = form.cleaned_data['language']

        obj_word = Word.objects.get(pk=self.request.session['last_word'][2])

        if lan == 'en' and transfer == obj_word.transfer:
            self.true_ans += 1
            return True
        elif lan == 'ru' and transfer == obj_word.word:
            self.true_ans += 1
            return True
        else:
            ValueError('Что-то пошло не так в en_dict.utilites.check_transfer')

    def get_word(self, words, last=False):
        """Возвращает кортеж из случайного поля word_obj и языка его символов
           Если last=True, просто возвращает предыдущий кортеж, возвращаемый этим методом
        """
        if last:
            return self.request.session.get('last_word')

        word_obj = get_random_obj(words)
        self.pk_ans_words.append(word_obj.pk)
        self.count_ans += 1

        WordObj = namedtuple('Word_obj', 'word lan pk')
        r = choice(('en', 'ru'))  # for random

        if r == 'en':
            self.request.session['last_word'] = WordObj(word_obj.word, 'en', word_obj.pk)
            return self.request.session['last_word']
        elif r =='ru':
            self.request.session['last_word'] = WordObj(word_obj.transfer, 'ru', word_obj.pk)
            return self.request.session['last_word']
        else:
            raise ValueError('Что-то пошло не так в en_dict.utilites.get_word')

    def del_session(self):
        """Удаляет все сессии трени"""
        self.pk_ans_words = []
        self.true_ans = 0
        self.count_ans = 0

    def get_context(self, over=False, **kwargs):
        """Возвращает контекст"""
        if over:
            context = {'cnt': self.count_ans,
            'true_answer': self.true_ans,
            'true_percent': get_percent(self.true_ans, self.count_ans),
            }
            return context

        context = {'cnt': self.count_ans,
            'true_answer': self.true_ans,
            'true_percent': get_percent(self.true_ans, self.count_ans),
            'form': kwargs.pop('form'),
            'word': self.request.session.get('last_word')[0],
            }
        return context
    
    def save_session_training(self):
        print(self.pk_ans_words)
        self.request.session['pk_ans_words'] = self.pk_ans_words
        self.request.session['true_ans'] = self.true_ans
        self.request.session['count_ans'] = self.count_ans
        self.request.session.modified = True

    def get_text_message(self, error=False):
        """Случайное сообщение"""
        word_obj = Word.objects.get(pk=self.request.session['last_word'][2])

        if error:
            return 'Неправильно... {} < ----- > {}'.format(word_obj.word, word_obj.transfer)
        return 'Все верно! ... {} < ----- > {}'.format(word_obj.word, word_obj.transfer)
