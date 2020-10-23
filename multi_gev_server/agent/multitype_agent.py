from agent_base import Agent
from CardEvaluator.lookup import lookup
import random

def clip_pot(a, cl, ch):
    if a < cl:
        return cl
    if a > ch:
        return ch
    return a

def get_last_round_raised(data):
    result = []
    for i, one_round in enumerate(data["action_history"]):
        rmax = 0
        if i == 0:
            rmax = 100
        for one_action in one_round:
            # p, a = one_action.split(":")
            a = one_action['action']
            if a[0] == "r":
                rmax = max(rmax, int(a[1:]))
        result.append(rmax)
    return sum(result[:-1])

def get_hand_strength(data):
    private_card = data['private_card']
    public_card = data['public_card']
    hand_strength = lookup.calc(private_card, public_card)
    return hand_strength

class HotheadManiac(Agent):
    """ HM  总是随机raise 0.5/1 pot
    """
    def get_action(self, data):
        last_round_raise = get_last_round_raised(data)
        self.position = data['position']
        if 'raise' in data['legal_actions']:
            raise_range_low, raise_range_high = data['raise_range']
            opponent_bet = max(data['players'][position]['total_money'] - data['players'][position]['money_left'] for position in range(len(data['players'])))
            pot = opponent_bet * 2
            pot = [pot // 2, pot]
            
            raise_number = opponent_bet + pot[random.randint(0, 1)] - last_round_raise
            raise_nums = clip_pot(raise_number, raise_range_low, raise_range_high)

            action = 'r' + str(raise_nums)
        elif 'call' in data['legal_actions']:
            action = 'call'
        else:
            action = 'check'
        return action


class HandStrengthAgent(Agent):
    def get_hand_strength_band(self):
        return NotImplemented

    def get_action(self, data):
        hand_strength_band_low, hand_strength_band_high = self.get_hand_strength_band()
        last_round_raise = get_last_round_raised(data)
        hand_strength = get_hand_strength(data)
        if hand_strength < hand_strength_band_low and ('fold' in data['legal_actions']):
            return 'fold'
        elif hand_strength < hand_strength_band_high:
            if 'call' in data['legal_actions']:
                return 'call'
            else:
                return 'check'
        elif hand_strength > hand_strength_band_high:
            if 'raise' in data['legal_actions']:
                self.position = data['position']
                raise_range_low, raise_range_high = data['raise_range']
                opponent_bet = max(data['players'][position]['total_money'] - data['players'][position]['money_left'] for position in range(len(data['players'])))
                pot = opponent_bet * 2
                pot = [pot // 4, pot]
                raise_number = opponent_bet + random.randrange(pot[0], pot[1]) - last_round_raise
                raise_nums = clip_pot(raise_number, raise_range_low, raise_range_high)
                return 'r' + str(raise_nums)
            elif 'call' in data['legal_actions']:
                return 'call'
            else:
                return 'check'
        else:
            if 'call' in data['legal_actions']:
                return 'call'
            else:
                return 'check'


class CandidStatistician(HandStrengthAgent):
    """ CS 弱牌fold，中间call/check, 好牌根据牌力bet 1/4 - 1 pot
        The Candid Statistician’s moves always reflect its hand strength. Bluffing can be
        effective when the Candid Statistician holds a weak hand
    """
    def get_hand_strength_band(self):
        return (-100, 100)


class LooseAggressive(HandStrengthAgent):
    """ LA 对于较大范围的手牌进行raise
    """
    def get_hand_strength_band(self):
        return (-100, -300)


class LoosePassive(HandStrengthAgent):
    """ LP 对于大部分牌都call，弱牌fold, 很少raise
    """
    def get_hand_strength_band(self):
        return (-300, 500)


class TightPassive(HandStrengthAgent):
    """ TP 对于大部分‘好’牌都call，大部分牌fold, 很少raise
    """
    def get_hand_strength_band(self):
        return (100, 500)


class RandomGambler(HandStrengthAgent):
    """ RG 每隔50局游戏更改自己的策略
    """
    def get_hand_strength_band(self):
        hand_strength_band_list = [
            (-100, 100),
            (-100, -300),
            (-300, 500),
            (100, 500)
        ]
        if self.game_counter % 50 == 0:
            self.cur_id = random.randint(0, 3)
        return hand_strength_band_list[self.cur_id]


class ScaredLimper(Agent):
    """ SL 只有拿到最顶级的牌才call，否则对于任何bet都fold        
        The Scared Limper always calls the big blind when being the small blind and folds
        to almost any raise at any stage of the game unless holding top hands (i.e. winning
        probability close to one). 
    """
    hand_strength_band = 200

    def get_action(self, data):
        hand_strength = get_hand_strength(data)
        # 小盲时，直接call
        if data["action_history"][-1] == []:
            if 'call' in data['legal_actions']:
                action = 'call'
            else:
                action = 'check'
            return action 

        
        opponent_bet = max(data['players'][position]['total_money'] - data['players'][position]['money_left'] for position in range(len(data['players'])))
        last_round_raise = get_last_round_raised(data)
                
        if opponent_bet != last_round_raise:
            if (hand_strength < self.hand_strength_band):
                return 'fold'

        if 'call' in data['legal_actions']:
            action = 'call'
        else:
            action = 'check'
        return action


class TightAggressive(Agent):

    hand_strength_band_high = 100     # 用于调整手牌阈值
    hand_strength_band_low = -100
    bluffing_rate = 0.2  #弱牌bluffing的概率

    def get_action(self, data):
        self.position = data['position']
        last_round_raise = get_last_round_raised(data)
        hand_strength = get_hand_strength(data)
        if hand_strength < self.hand_strength_band_low :
            rand_num = random.uniform(0, 1)
            # bluffing
            if (rand_num < self.bluffing_rate) and ('raise' in data['legal_actions']):
                raise_range_low, raise_range_high = data['raise_range']


                opponent_bet = max(data['players'][position]['total_money'] - data['players'][position]['money_left'] for position in range(len(data['players'])))
                pot = opponent_bet * 2
                pot = [pot // 4, pot]
                raise_number = opponent_bet + random.randrange(pot[0], pot[1]) - last_round_raise

                raise_nums = clip_pot(raise_number, raise_range_low, raise_range_high)
                
                return 'r' + str(raise_nums)

            elif 'fold' in data['legal_actions']:
                return 'fold'

        elif hand_strength < self.hand_strength_band_high:
            if 'call' in data['legal_actions']:
                return 'call'
            else:
                return 'check'
        elif hand_strength > self.hand_strength_band_high:
            if 'raise' in data['legal_actions']:

                raise_range_low, raise_range_high = data['raise_range']

                opponent_bet = max(data['players'][position]['total_money'] - data['players'][position]['money_left'] for position in range(len(data['players'])))
                pot = opponent_bet * 2
                pot = [pot // 4, pot]

                raise_number = opponent_bet + random.randrange(pot[0], pot[1]) - last_round_raise

                raise_nums = clip_pot(raise_number, raise_range_low, raise_range_high)

                return 'r' + str(raise_nums)
            elif 'call' in data['legal_actions']:
                return 'call'
            else:
                return 'check'
        else:
            if 'call' in data['legal_actions']:
                return 'call'
            else:
                return 'check'

    
if __name__ == "__main__":
    # agent = CandidStatistician(1000000, 3, "CallAgent", 3, "holdem.ia.ac.cn", 18888, ["CallAgent", "CallAgent"], verbose=True)
    # agent.run()
    
    # agent = HotheadManiac(1000001, 3, "CallAgent", 3, "holdem.ia.ac.cn", 18888, ["CallAgent", "CallAgent"], verbose=True)
    # agent.run()

    # agent = LooseAggressive(1000002, 3, "CallAgent", 3, "holdem.ia.ac.cn", 18888, ["CallAgent", "CallAgent"], verbose=True)
    # agent.run()

    # agent = LoosePassive(1000003, 3, "CallAgent", 3, "holdem.ia.ac.cn", 18888, ["CallAgent", "CallAgent"], verbose=True)
    
    # agent = TightAggressive(1000004, 3, "CallAgent", 3, "holdem.ia.ac.cn", 18888, ["CallAgent", "CallAgent"], verbose=True)
    # agent.run()

    # agent = ScaredLimper(1000005, 3, "CallAgent", 3, "holdem.ia.ac.cn", 18888, ["CallAgent", "CallAgent"], verbose=True)
    # agent.run()

    agent = RandomGambler(1000006, 2, "CallAgent", 1, "holdem.ia.ac.cn", 18888, ["CandidStatistician"], verbose=True)
    agent.run()

    # agent = TightPassive(1000007, 3, "CallAgent", 3, "holdem.ia.ac.cn", 18888, ["CallAgent", "CallAgent"], verbose=True)
    # agent.run()

