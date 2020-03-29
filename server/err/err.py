class RoomNotExistException(Exception):
    error_text = {
        'info': 'error',
        'text': 'room not exists'
    }


class RoomFullException(Exception):
    error_text = {
        'info': 'error',
        'text': 'room is full'
    }


class DisconnectException(Exception):
    error_text = {
        'info': 'error',
        'text': 'Some players are disconnected'
    }
