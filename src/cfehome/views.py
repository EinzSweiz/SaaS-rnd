from django.http import HttpResponse
from django.shortcuts import render
import pathlib
from django.contrib.auth.decorators import login_required
from visits.models import PageVisit 
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings


LOGIN_URL = settings.LOGIN_URL

def home_page_view(request, *args, **kwargs):

    qs = PageVisit.objects.all()
    page_qs = PageVisit.objects.filter(path=request.path)
    page_visit = PageVisit(path=request.path)
    page_visit.save()
    return render(request, 'index.html', {'title': 'Home Page', 'qs': qs.count(), 'page_qs': page_qs.count()})

ACCESS_PW = 'abc123'

def pw_protected_view(request, *args, **kwargs):
    is_allowed = request.session.get('protected_page_allowed') or 0
    if request.method == 'POST':
        user_pw_sent = request.POST.get('code')
        if user_pw_sent == ACCESS_PW:
            is_allowed = 1
            request.session['protected_page_allowed'] = is_allowed
    if is_allowed:
        return render(request, 'protected/view.html', {})
    return render(request, 'protected/entry.html', {})


@login_required
def user_only_view(request, *args, **kwargs):
    return render(request, 'protected/user-only.html', {})


@staff_member_required(login_url=LOGIN_URL)
def staff_only_view(request):
    return render(request, 'protected/user-only.html', {})
