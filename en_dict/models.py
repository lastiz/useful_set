from django.db import models
from users.models import AdvUser


class Word(models.Model):
    """Слово в базе"""
    owner = models.ForeignKey(AdvUser, related_name='words', on_delete=models.CASCADE)
    word = models.CharField(max_length=30, verbose_name='Слово', db_index=True, )
    transfer = models.CharField(max_length=30, verbose_name='Перевод', db_index=True, )

    class Meta:
        verbose_name = 'Слово'
        verbose_name_plural = 'Слова'
        ordering = ['word', ]

    def __str__(self):
        return self.word
