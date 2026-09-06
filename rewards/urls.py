from django.urls import path
from . import views

app_name = "rewards"

urlpatterns = [
    path("my-rewards/", views.my_rewards, name="my_rewards"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
]
