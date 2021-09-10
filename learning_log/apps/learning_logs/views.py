from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib.auth.models import User
from .models import Topic, Entry
from .forms import TopicForm, EntryForm

# Create your views here.

def check_topic_owner(request, topic):
    # Проверяет, является ли текущий пользователь владельцем темы
    if not topic.owner == request.user:
        raise Http404

def index(request):
    # Представление домашней страницы Learning Log
    return render(request, 'learning_logs/index.html')

def topics(request):
    # Представление страницы тем.
    topics = Topic.objects.order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)


def topic(request, topic_id):
    # Представление странциы отдельной темы
    topic = get_object_or_404(Topic, id=topic_id)
    # Проверка того, что тема принаджлежит текущему пользователю
    #check_topic_owner(request, topic)
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    # Страница создания новой темы
    if request.method != 'POST':
        # Если запрос не отправляется на сервер, создается пустая форма
        form = TopicForm()
    else:
        # Если запрос отравляется, сохранятся новая тема
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')
    # Вывод пустой или недействительной формы
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):

    topic = Topic.objects.get(id=topic_id)
    check_topic_owner(request, topic)
    if request.method != 'POST':

        form = EntryForm()
    else:

        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)

    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):

    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    check_topic_owner(request, topic)
    if request.method != 'POST':

        form = EntryForm(instance=entry)
    else:

        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)

    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)


@login_required
def user_page(request, user_id):

    user = get_object_or_404(User, id=user_id)
    topics = Topic.objects.filter(owner=user)
    context = {'topics': topics, 'user': user}
    return render(request, 'learning_logs/user_page.html', context)

