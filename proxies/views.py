from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from .utilites.proxy_list import scrap_for_la_project


class IndexView(LoginRequiredMixin, TemplateView):
    """Home proxies"""
    template_name = 'proxies/index.html'


@login_required
def proxies_list(request):
    proxies = [item.split(':') for item in scrap_for_la_project()]
    paginator = Paginator(proxies, 20)
    page_num = request.GET.get('page', 1)
    page = paginator.get_page(page_num)
    context = {'proxies': page.object_list,
               'page': page,
               'is_paginated': page.has_other_pages()}
    return render(request, 'proxies/proxies_list.html', context)