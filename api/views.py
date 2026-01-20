from rest_framework import viewsets, permissions, authentication
from django.utils import timezone
from django.shortcuts import render,  redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Max

from .serializers import *


class CsrfExemptSessionAuthentication(authentication.SessionAuthentication):
    def enforce_csrf(self, request): return


def get_player_or_create(user):
    player, _ = Player.objects.get_or_create(user=user)
    player.last_seen = timezone.now()
    player.save(update_fields=['last_seen'])
    return player


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Player.objects.all().order_by('-score')
    serializer_class = PlayerSerializer


class SnakeScoreViewSet(viewsets.ModelViewSet):
    serializer_class = SnakeScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self): return SnakeScore.objects.filter(user=self.request.user).order_by('-score')

    def perform_create(self, serializer): serializer.save(user=self.request.user)


class ClickerScoreViewSet(viewsets.ModelViewSet):
    authentication_classes = [CsrfExemptSessionAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClickerScoreSerializer

    def get_queryset(self): return ClickerScore.objects.filter(player__user=self.request.user)

    def perform_create(self, serializer): serializer.save(player=get_player_or_create(self.request.user))


class NeTankScoreViewSet(viewsets.ModelViewSet):
    authentication_classes = [CsrfExemptSessionAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NeTankScoreSerializer

    def get_queryset(self): return NeTankScore.objects.filter(player__user=self.request.user)

    def perform_create(self, serializer): serializer.save(player=get_player_or_create(self.request.user))


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self): return Task.objects.filter(player__user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer): serializer.save(player=get_player_or_create(self.request.user))






@login_required
def main_menu_view(request):
    p, created = Player.objects.get_or_create(user=request.user)
    p.last_seen = timezone.now()
    p.save(update_fields=['last_seen'])

    best_snake = SnakeScore.objects.filter(user=request.user).aggregate(Max('score'))['score__max'] or 0
    best_tank = NeTankScore.objects.filter(player=p).aggregate(Max('score'))['score__max'] or 0
    best_1s = ClickerScore.objects.filter(player=p, mode='1s').aggregate(Max('cps'))['cps__max'] or 0
    best_10s = ClickerScore.objects.filter(player=p, mode__in=['10s', '10']).aggregate(Max('score'))['score__max'] or 0

    players = Player.objects.all().order_by('-score')[:10]
    top_snake_players = User.objects.annotate(max_score=Max('snake_scores__score')).filter(
        max_score__isnull=False).order_by('-max_score')[:10]
    top_clicker_players = Player.objects.annotate(max_score=Max('clicker_scores__score')).filter(
        max_score__isnull=False).order_by('-max_score')[:10]
    top_tank_players = Player.objects.annotate(max_score=Max('netank_scores__score')).filter(
        max_score__isnull=False).order_by('-max_score')[:10]

    return render(request, 'api/main_menu.html', {
        'best_snake': int(best_snake),
        'best_tank': int(best_tank),
        'best_1s_cps': round(float(best_1s), 2),
        'best_10s_score': int(best_10s),
        'players': players,
        'top_snake_players': top_snake_players,
        'top_clicker_players': top_clicker_players,
        'top_tank_players': top_tank_players,
        'current_player': p
    })


@login_required
def kanban_view(request):
    p = get_player_or_create(request.user)
    if request.method == 'POST':
        Task.objects.create(player=p, title=request.POST.get('title'), description=request.POST.get('description', ''),
                            status=request.POST.get('status', 'todo'))
        return redirect('kanban')
    tasks = Task.objects.filter(player=p).order_by('-created_at')
    return render(request, 'api/kanban.html', {'tasks': tasks})


@login_required
def tank_game_view(request):
    get_player_or_create(request.user)
    return render(request, 'api/tetris_tanks.html')


@login_required
def snake_flappy_view(request):
    get_player_or_create(request.user)
    return render(request, 'api/snake_flappy.html')


@login_required
def clicker_view(request):
    get_player_or_create(request.user)
    return render(request, 'api/clicker.html')


@login_required
def players_list_view(request):
    players = Player.objects.all().order_by('-score')
    return render(request, 'api/players_list.html', {'players': players})

@login_required
def task_detail_view(request, task_id):

    task = get_object_or_404(Task, id=task_id, player__user=request.user)
    return render(request, 'api/task_detail.html', {'task': task})





def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password1')
        u = User.objects.create_user(username=username, password=password)
        Player.objects.create(user=u)
        login(request, u)
        return redirect('main_menu')
    return render(request, 'api/register.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def login_view(request):
    from django.contrib.auth.views import LoginView
    return LoginView.as_view(template_name='api/login.html', redirect_authenticated_user=True)(request)
