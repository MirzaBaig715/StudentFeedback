from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from analytics.libs.db_helper import Timeline

from analytics.libs.drilldown_chart import Graphable
from feedback.models import Faculty, ClassFacSub, Feedback
from .libs import tree_builder, graph_builder
from StudentFeedback.settings import DIRECTOR_GROUP
from analytics.libs import db_helper
from analytics.libs.faculty_graphs import faculty_graph, class_sub_graph, timeline_graph


@login_required
def director(request, category, year, branch, sub, subsub):

    if not request.user.groups.filter(name=DIRECTOR_GROUP).exists():
        return render(request, 'feedback/invalid_user.html')

    template = 'analytics/director.html'
    context = {'category': category, 'year': year, 'branch': branch, 'sub': sub, 'subsub': subsub,
               'year_objs': tree_builder.getTree(), 'active': 'home'}
    graph_type = 'null'
    if request.method == 'POST':
        for typ in graph_builder.Graph.types:
            if typ in request.POST:
                graph_type = typ
                break

    context['graph'] = graph_builder.Graph(category, year, branch, sub, subsub, graph_type=graph_type)

    context['facultys'] = db_helper.get_all_faculty()


    return render(request, template, context)


@login_required
def faculty_info(request):

    if not request.user.groups.filter(name=DIRECTOR_GROUP).exists():
        return render(request, 'feedback/invalid_user.html')

    if request.method == 'POST':
        if 'faculty' in request.POST:

            context = {}
            faculty = request.POST.getlist('faculty')[0]
            try:
                faculty = Faculty.objects.get(name=faculty)
            except:
                context['error'] = "Sorry, the faculty: "+faculty+' is not found'
                return render(request, 'analytics/faculty.html', context)

            context['faculty'] = faculty
            context['facultys'] = db_helper.get_all_faculty()

            context['graph'] = faculty_graph.FacultyGraph(faculty=faculty.name)
            context['graph2'] = class_sub_graph.ClassSubGraph(faculty=faculty.name)
            context['graph3'] = timeline_graph.TimelineGraph(faculty=faculty.name)

            return render(request, 'analytics/faculty.html', context)
    else:
        return redirect('/')