from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import *
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(title="GAME API", default_version='v2'),
   public=True,
)

router = DefaultRouter()
router.register(r'players', PlayerViewSet)
router.register(r'clicker_scores', ClickerScoreViewSet, basename='clicker_scores')
router.register(r'tasks', TaskViewSet, basename='tasks')


router.register(r'ne_tank', NeTankScoreViewSet, basename='ne_tank')
router.register(r'snake_scores', SnakeScoreViewSet, basename='snake_scores')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('', main_menu_view, name='main_menu'),
    path('snake-flappy/', snake_flappy_view, name='snake_flappy'),
    path('clicker/', clicker_view, name='clicker'),
    path('ne-tank/', tank_game_view, name='ne_tank'),
    path('kanban/', kanban_view, name='kanban'),
    path('players/', players_list_view, name='players_list'),
    path('task/<int:task_id>/', task_detail_view, name='task_detail'),

    path('api/', include(router.urls)),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
