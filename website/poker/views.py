from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import django.contrib.auth
from django.urls import reverse
from .models import Room, Room_Person
from dwebsocket import accept_websocket, require_websocket
import socket
# Create your views here.

import json
import struct 

def sendJson(request, jsonData):
    data = json.dumps(jsonData).encode()
    request.send(struct.pack('i', len(data)))
    request.sendall(data)
  

def recvJson(request):
    l = struct.unpack('i', request.recv(4))[0]
    data = json.loads(request.recv(l).decode())
    return data
   
def test(request):
    return render(request, "test.html", locals()) 

@require_websocket
def test_recv(request):
    while (1):
        import time
        time.sleep(1)
        request.websocket.send("Hello World")
    # message = request.websocket.wait()

def base(request):
    return render(request, "base.html", locals())

def login(request):
    return render(request, "login.html", locals())

def login_solve(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(username=username, password=password)
    if user is not None and user.is_active:
        django.contrib.auth.login(request, user)
        request.session['username'] = username
        return HttpResponse(1)
    else:
        return HttpResponse(2)

def register(request):
    return render(request, "register.html", locals())

def register_solve(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    try:
        user = User.objects.create_user(username=username, password=password)
    except Exception as e:
        return HttpResponse(2)
    return HttpResponse(1)

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('poker:login'))
    try:
        username = request.session['username']
    except:
        return HttpResponseRedirect(reverse('poker:login'))
    rooms = Room.objects.all()
    for room in rooms:
        cur_people = len(Room_Person.objects.filter(room=room))
        room.full = cur_people == room.max_people
    return render(request, "index.html", locals())

def create_room(request):
    name = request.POST.get('name')
    max_num = request.POST.get('num')
    bot_num = request.POST.get('bot_num')
    person = User.objects.get(username=request.session['username'])
    room = Room(name=name, max_people=int(max_num), bot_num=int(bot_num))
    room.save()
    room_person = Room_Person(room=room, person=person, seq_id=0)
    room_person.save()
    global room_socket
    try:
        room_socket 
    except:
        room_socket = {}
    room_socket[room.pk] = []
    return HttpResponse(room.id)

def enter_room(request):
    room_id = int(request.POST.get("room_id"))
    person = User.objects.get(username=request.session['username'])
    room = Room.objects.get(pk=room_id)
    cur_people = len(Room_Person.objects.filter(room=room))
    room_person = Room_Person(room=room, person=person, seq_id=cur_people)
    room_person.save()
    return HttpResponse(1)

def room_hall(request, room_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('poker:login'))
    try:
        username = request.session['username']
    except:
        return HttpResponseRedirect(reverse('poker:login'))
    room = Room.objects.get(pk=room_id)
    people = Room_Person.objects.filter(room=room)
    return render(request, "room.html", locals())

def room_hall_leave_room(request, room_id):
    person = User.objects.get(username=request.session['username'])
    room = Room.objects.get(pk=room_id)
    num = len(Room_Person.objects.filter(room=room))
    Room_Person.objects.get(room=room, person=person).delete()
    if num == 1:
        room.delete()
    return HttpResponse(1)

@accept_websocket
def room_hall_ws(request, room_id):
    room_socket[room_id].append(request.websocket)
    while (1):
        message = request.websocket.wait().decode()
        print(message)
        if message == "exit":
            break
        elif message == "start":
            room = Room.objects.get(pk=room_id)
            room.start = True
            room.save(  )
            for socket in room_socket[room_id]:
                socket.send("start")
    request.websocket.close()

def room_game(request, room_id):
    person = User.objects.get(username=request.session['username'])
    room = Room.objects.get(pk=room_id)
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('poker:login'))
    try:
        username = request.session['username']
    except:
        return HttpResponseRedirect(reverse('poker:login'))
    room = Room.objects.get(pk=room_id)
    people = Room_Person.objects.filter(room=room)
    max_people = room.max_people
    return render(request, "game.html", locals())

@accept_websocket
def room_game_ws(request, room_id):
    import json
    import time
    room = Room.objects.get(pk=room_id)
    max_people = room.max_people
    bot_num = room.bot_num
    person = User.objects.get(username=request.session['username'])
    ws = request.websocket
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
    client.connect(('aa.xuhang.ink', 18888))
    bots = []
    for i in range(bot_num):
        import random
        if random.randint(0, 1) == 0:
            bots.append('CallAgent')
        else:
            bots.append('RandomAgent')
    message = dict(info='connect', room_id=room_id, name=person.username, room_number=max_people, bots=bots)
    sendJson(client, message)
    data = recvJson(client)
    ws.send(json.dumps(data))
    sendJson(client, {'info': 'start'})
    while (1):
        data = recvJson(client)
        ws.send(json.dumps(data))
        if data['info'] == 'state' and data['position'] == data['action_position'] or data['info'] == 'result':    
            data = json.loads(ws.wait().decode())
            sendJson(client, data)

def room_observe(request, room_id):
    return render(request, "observe.html", locals())


@accept_websocket
def room_observe_ws(request, room_id):
    import json
    import time
    ws = request.websocket
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
    client.connect(('aa.xuhang.ink', 18888)) 
    message = dict(info='observer', room_id=room_id)
    sendJson(client, message)
    first_people = None
    while (1):
        data = recvJson(client)
        if first_people is None:
            first_people = data['name'][0]
        while data['name'][0] != first_people:
            obj = data['name'].pop(0)
            data['name'].append(obj)
            if data['info'] == 'state':
                rotate_position(data, ['player_card', 'round_raise', 'money'])
                if data['action_player'] != "":
                    data['action_player'] = (data['action_player'] + len(data['name']) - 1) % len(data['name'])
                    data['action_position'] = (data['action_position'] + len(data['name']) - 1) % len(data['name'])
            else:
                rotate_position(data, ['total_money', 'times', 'player_card', 'win_money'])
        ws.send(json.dumps(data))

def rotate_position(data, keys):
    for key in keys:
        obj = data[key].pop(0)
        data[key].append(obj)