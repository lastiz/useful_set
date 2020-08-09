from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q

from .models import Word
from .forms import WordAddForm, WordEnterForm
from .utilites import Training


class IndexListView(LoginRequiredMixin ,ListView):
    """Домашнаяя, выводит все слова в словаре у пользователя"""
    template_name = 'en_dict/index.html'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Word.objects.only('word', 'transfer').filter(users=self.user_id)
    
    


class WordAddView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    """Доб. слова в словарь пользователя"""

    template_name = 'en_dict/word_add.html'
    form_class = WordAddForm
    success_url = reverse_lazy('en_dict:add_word')
    success_message = 'Слово успешно добавлено'

    def dispatch(self, request, *args, **kwargs):
        """Получаем текущего пользователя"""
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)
    
    def get_initial(self):
        return {'user_id': self.user_id, }


@login_required            
def training(request):
    """Тренировка"""
    training_obj = Training(request)

    if request.GET.get('new', False) and request.method != 'POST':  # заново
        training_obj.del_session()

    q = Q(users=request.user.pk) & ~Q(pk__in=training_obj.pk_ans_words)  # все слова пользователя, не входящие в отгаданные 
    words = Word.objects.only('word', 'transfer').filter(q)

    if request.method != 'POST':
        if words and training_obj.count_ans <= 50:
            form = WordEnterForm(word=training_obj.get_word(words))

        else:  # тренировка окончена
            context = training_obj.get_context(over=True)  # иначе del_session 
            training_obj.del_session()
            return render(request, 'en_dict/training_over.html', context)
    
    else:
        form = WordEnterForm(data=request.POST, word=training_obj.get_word(words, last=True))

        if form.is_valid():
            if training_obj.check_transfer(form):
                messages.success(request, training_obj.get_text_message())
            else:
                messages.error(request, training_obj.get_text_message(error=True))

            training_obj.save_session_training()  # записываем сессии
            return redirect('en_dict:training')
    
    training_obj.save_session_training()
    return render(request, 'en_dict/training.html', training_obj.get_context(form=form))

