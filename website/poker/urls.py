from django.urls import path 
from . import views

app_name = 'poker'
urlpatterns = [
    path('base/', views.base, name="base"),
    path('', views.index, name="index"),
    
    path('login/', views.login, name="login"),    
    path('login/solve/', views.login_solve),
    
    path('register/', views.register, name="register"),
    path('register/solve/', views.register_solve),
    
    path('create_room/', views.create_room),
    path('enter_room/', views.enter_room),

    path('room/<int:room_id>/', views.room_hall, name='room_hall'),
    path('room/<int:room_id>/leave_room/', views.room_hall_leave_room),
    path('room/<int:room_id>/ws/', views.room_hall_ws),

    path('test/', views.test),
    path('test/recv/', views.test_recv),

    path('room/<int:room_id>/game/', views.room_game, name='room_game'),
    path('room/<int:room_id>/game/ws/', views.room_game_ws),

    path('room/<int:room_id>/observe/', views.room_observe, name='observe'),
    path('room/<int:room_id>/observe/ws/', views.room_observe_ws),
]
