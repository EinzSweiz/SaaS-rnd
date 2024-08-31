from django.http import HttpResponse
from django.shortcuts import render
import pathlib
from visits.models import PageVisit 


def home_page_view(request, *args, **kwargs):

    qs = PageVisit.objects.all()
    page_qs = PageVisit.objects.filter(path=request.path)
    page_visit = PageVisit(path=request.path)
    page_visit.save()
    return render(request, 'index.html', {'title': 'Home Page', 'qs': qs.count(), 'page_qs': page_qs.count()})
