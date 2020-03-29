class Round():
    def __init__(self, num_players, big_blind):
        self.num_players = num_players
        self.big_blind = big_blind

    def round_init(self, pointer, iniitial_raised_counter = None):
        self.pointer = pointer
        if iniitial_raised_counter is not None:
            self.raised_counter = iniitial_raised_counter
        else:
            self.raised_counter = [0 for _ in range(self.num_players)]
        self.call_count = 0

    def step(self, players, dealer, action):
        player = players[self.pointer]
        if action == 'call':
            self.call_count += 1
            max_raise = max(self.raised_counter)
            player.wager(max_raise - self.raised_counter[self.pointer], dealer)
            self.raised_counter[self.pointer] = max_raise
        
        elif action == 'check':
            self.call_count += 1
        
        elif action[0] == 'r':
            action = int(action[1:])
            self.call_count = 1
            player.wager(action - self.raised_counter[self.pointer], dealer)
            self.raised_counter[self.pointer] = action

        elif action == 'fold':
            self.call_count += 1
            player.status = 'folded'
        
        self.get_next_player(players)
        return self.pointer
    
    def get_next_player(self, players):
        self.pointer = (self.pointer + 1) % self.num_players
        while players[self.pointer].status == 'folded' and self.call_count < self.num_players:
            self.call_count += 1
            self.pointer = (self.pointer + 1) % self.num_players

    def get_legal_actions(self, players):
        '''返回玩家可以进行的合法动作.

        Return:
            legal_actions, 合法动作，包括call, check, fold, raise
            raise_range, raise的范围(该轮金额)(raise to)，当合法动作包含raise时有意义 
        '''
        player = players[self.pointer]
        have_raised = self.raised_counter[self.pointer]
        legal_actions = ['fold']
        if self.raised_counter[self.pointer] == max(self.raised_counter):
            legal_actions.append('check')
        if self.raised_counter[self.pointer] < max(self.raised_counter):
            legal_actions.append('call')
    
        # 计算需要补齐的差价
        diff = max(self.raised_counter) - have_raised
        raise_range = []
        # 如果在补齐差价后还有钱，则可以进行raise操作
        if player.remained_chips > diff:
            legal_actions.append('raise')
            # 额外raise的最小金额为大盲和两次差价的较大值
            min_raise_amount = max(self.big_blind, diff) + diff
            if min_raise_amount > player.remained_chips:
                raise_range.append(player.remained_chips + have_raised)
                raise_range.append(player.remained_chips + have_raised)           
            else:
                raise_range.append(have_raised + min_raise_amount)
                raise_range.append(have_raised + player.remained_chips)
        return legal_actions, raise_range
        

    def is_terminal(self):
        return self.call_count == self.num_players