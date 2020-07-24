class MyError(Exception):
    pass


class RoomNotExitError(MyError):
    def __init__(self, room_id):
        self.text = {
            'info': 'error',
            'text': 'room not exists',
            'op_type': 'room',
            'room_id': room_id
        }


class RoomFullError(MyError):
    def __init__(self, room_id, uuid):
        self.text = {
            'info': 'error',
            'text': 'room is full',
            'op_type': 'player',
            'uuid': uuid,
            'room_id': room_id,
        }


class DisconnectError(MyError):
    def __init__(self, room_id):
        self.text = {
            'info': 'error',
            'text': 'Some players are disconnected',
            'op_type': 'room',
            'room_id': room_id
        }


class PlayCompeleteError(MyError):
    def __init__(self, room_id):
        self.text = {
            'info': 'success',
            'text': 'Complete playing',
            'op_type': 'room',
            'room_id': room_id
        }


class PlayerExitError(MyError):
    def __init__(self, room_id):
        self.text = {
            'info': 'error',
            'text': 'Some players exit the room',
            'op_type': 'room',
            'room_id': room_id
        }


class AgentNotFoundError(MyError):
    def __init__(self, room_id, agent_name):
        self.text = {
            'info': 'error',
            'text': 'Agent {} not found'.format(agent_name),
            'op_type': 'room',
            'room_id': room_id
        }


class NoEnoughResource(MyError):
    def __init__(self, room_id, agent_name):
        self.text = {
            'info': 'error',
            'text': 'No enough resources for agent {}'.format(agent_name),
            'op_type': 'room',
            'room_id': room_id
        }

class InvalidActionError(MyError):
    def __init__(self, action, player_id=None, room_id=None):
        self.text = {
            'info': 'error',
            'text': 'Invalid action: {}'.format(action)
        }
        self.action = action
        if player_id is not None:
            self.text["room_id"] = room_id
            self.text["uuid"] = player_id
            self.text["op_type"] = "room"