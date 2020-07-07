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
