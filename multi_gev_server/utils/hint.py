play_compelete_info = {
    'info': 'success',
    'text': 'Complete playing',
}

def  room_full_info(room_id):
    return {
        'info': 'error',
        'text': 'room {} is full'.format(room_id)
    }            

def invalid_action_info(name, action):
    return {
        'info': 'error',
        'text':'Player {} makes an illegal action: {}'.format(name, action)
    }

def disconnect_info(name):
    return {
        'info': 'error',
        'text': 'Player {} disconnected'.format(name)
    }

def player_exit_info(name):
    return {
        'info': 'error',
        'text': 'Player {} exit the room'.format(name)
    }

def agent_not_found_info(agent_name):
    return {
        'info': 'error',
        'text': 'Agent {} not found'.format(agent_name),
    }

def room_not_exist_info(room_id):
    return {
        'info': 'error',
        'text': 'room {} not exists'.format(room_id),
    }

def unknown_error_info(info):
    return {
        'info': 'Unhandled error',
        'text':  info,
    }

def no_enough_resource_info(agent_name):
    return {
        'info': 'error',
        'text': 'No enough resources for agent {}'.format(agent_name)
    }
    
def no_action_info(name):
    return {
        'info': 'error',
        'text': 'No action in Player {}\' message'.format(name)
    }
    
