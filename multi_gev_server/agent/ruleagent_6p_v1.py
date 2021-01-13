import random
import numpy as np
import time
import sys
import json
import struct
import socket
import traceback
from agent_base import Agent


def handsrank1(hands):
    a=1#表示起手手牌的大小
    handsrank=[]
    handssuit=[]
    handsrank.append(hands[0][0])
    handsrank.append(hands[1][0])
    handssuit.append(hands[0][1])
    handssuit.append(hands[1][1])
    if kind(2,handsrank):
        if handsrank[0]>12:
            a=9
        elif handsrank[0]==11 or handsrank[0]==12:
            a=8
        elif handsrank[0]==10 or handsrank[0]==9 or handsrank[0]==8 :
            a=7
        elif handsrank[0]==7:
            a=6
        else:
            a=5
    elif kind(2,handssuit):
        if max(handsrank)==14:
            if min(handsrank)>11:
                a=8
            elif min(handsrank)<12 and min(handsrank)>9:
                a=7
            elif min(handsrank)==6  or min(handsrank)==7:
                a=5
            else:
                a=6
        elif max(handsrank)>11:
            if min(handsrank)>9:
                a=7
            elif min(handsrank)<10 and min(handsrank)>6:
                a=6
            else:
                a=5
        else:
            a=4
        if max(handsrank)-min(handsrank)==1:
            a=a+1
    else:
        if max(handsrank)>12:
            if min(handsrank)>11:
                a=8
            elif min(handsrank)<12 and min(handsrank)>9:
                a=7
            
            elif min(handsrank)==6  or min(handsrank)==7 or min(handsrank)==8:
                a=5
            else:
                a=4
        elif max(handsrank)<13 and max(handsrank)>10:
            if min(handsrank)>11:
                a=6
            elif min(handsrank)<12 and min(handsrank)>9:
                a=5
            elif min(handsrank)==6  or min(handsrank)==7:
                a=4
            else:
                a=3
        else:
            a=2
        if max(handsrank)-min(handsrank)<3:
            if max(handsrank)<12:
                a=a+1
        else:
            if max(handsrank)<11:
                a=a-1
    return a

def run1_1undergunblind(hands,opobet):#2轮即可，这个是第一轮
    a=random.random()
    b=0
    if opobet==0:
        b=1
    if handsrank1(hands)==9 and b==1:
        
        if a>0.985:
            action='call'
            bet=100
        else:
            action='raise'
            bet=300
    elif handsrank1(hands)==8 and b==1:
        
        if a>0.933:
            action='call'
            bet=100
        else:
            bet=300
            action='raise'
    elif handsrank1(hands)==7 and b==1:
        
        if a>0.873:
            action='call'
            bet=100
        else:
            bet=300
            action='raise'
    elif handsrank1(hands)>3 and handsrank1(hands)<7 and b==1:
        
        if a>0.896:
            action='check'
            bet=100

        else:
            action='fold'
            bet=0
  

    elif handsrank1(hands)==3 and b==1:
        
        if a>0.965:
            action='call'
            bet=100
        else:
            action='fold'
            bet=0
    elif handsrank1(hands)==2 and b==1:
        
        if a>0.992:
            action='call'
            bet=100
        else:
            action='fold'
            bet=0
    elif b==1:
        
        if a>0.997:
            action='call'
            bet=100
      
        else:
            action='fold'
            bet=0
    else:
        if handsrank1(hands)>7:
            if a>0.055:
                action='allin'
                bet=20000
            else:
                action='call'
                bet=3*opobet
        else:
            action='fold'
            bet=0
    return action,bet

def run1_1otherblind(hands,opobet):#2轮即可，这个是第一轮
    a=random.random()
    if handsrank1(hands)==9:
        
        if a>0.9735:
            action='call'
            bet=0
        else:
            action='raise'
            bet=opobet*3
            if opobet>1000:
                action='allin'
                bet=20000
    elif handsrank1(hands)==8:
        
        if a>0.9617:
            action='call'
            bet=0
        else:
            action='raise'
            bet=opobet*3
            if opobet>2000:
                action='allin'
                bet=20000
    elif handsrank1(hands)==7:
        
        if a>0.9228:
            action='call'
            bet=0
        else:
            action='raise'
            bet=opobet*2
            if opobet>2500:
                action='allin'
                bet=20000
    elif handsrank1(hands)==6:
        
        if a<0.9530:
            action='call'
            bet=0
        else:
            action='raise'
            bet=opobet*2
    elif handsrank1(hands)==5:
        
        if a<0.9787:
            action='call'
            bet=0
        else:
            action='raise'
            bet=opobet*2
    elif handsrank1(hands)==4:
        
        if a<0.98518:
            action='call'
            bet=0
        else:
            action='raise'
            bet=opobet*2
    elif handsrank1(hands)==3:
        
        if a<0.9906:
            action='call'
            bet=0
        else:
            action='raise'
            bet=opobet*2
    elif handsrank1(hands)==2:
        
        if a<0.9953:
            action='call'
            bet=0
        else:
            action='raise'
            bet=opobet*2
    else:
        

        action='call'
        bet=0
    return action,bet

def run1_2undergunblind(hands,optbet,selfbet):#2轮即可，这个是第一轮
    a=random.random()
    if handsrank1(hands)>7:#opo bet1*potsize
        action='raise'
        bet=optbet*7

    elif handsrank1(hands)<8 and handsrank1(hands)>5 :
        if optbet<selfbet*2:
            action='call'
            bet=0
        else:
            action='fold'
            bet=0
    else:
            action='fold'
            bet=0
    return action,bet

def run1_2otherblind(hands,optbet,selfbet):#2轮即可，这个是第一轮
    a=random.random()
    if handsrank1(hands)>7:#opo bet1*potsize
        action='raise'
        bet=optbet*3

    elif handsrank1(hands)<8 and handsrank1(hands)>4 :
        if optbet<selfbet:
            action='call'
            bet=0
        else:
            action='fold'
            bet=0
    else:
        action='fold'
        bet=0
    return action,bet

def kind(n, ranks):#判断有几张是一样的
  for s in ranks:
    if ranks.count(s) == n : return s
  return None#

def public3straight3(publicrank):#公共牌三顺
    publicrank.sort(reverse=True)
    if publicrank[0] - publicrank[2] == 2 and len(set(publicrank)) == 3:
        return publicrank[0]
    else:
        return 0

def handinpublicthreekill3(handsrank,publicrank):#2+3 3为3条 2中有一个和三条一样
    a=0
    for i in range(2):
        if handsrank[i][0]==publicrank[0][0]:
            a=1
    return a

def handinpubliconepair3(handsrank,publicrank):#2+3 的有三条或者四条
    a=0
    allrank=[]
    allrank.append(handsrank[0])
    allrank.append(handsrank[1])
    allrank.append(publicrank[0])
    allrank.append(publicrank[1])
    allrank.append(publicrank[2])
    if kind(3,allrank) or kind(4,allrank):
        a=1
    return a

def judgepublic3hand(publicrank,publicsuit):#2+3 3类型的判断
    if kind(3,publicrank):
        publicrank3type='three kill'
    elif kind(2,publicrank):
        publicrank3type='one pair'
    else:
        publicrank3type='norank'

    if kind(3,publicsuit):
        publicsuit3type='threesuits'
    elif kind(2,publicsuit):
        publicsuit3type='twosuits'
    else:
        publicsuit3type='nosuit'

    if public3straight3(publicrank)>0:
        publicstraight3type='threestraight'
    else:
        publicstraight3type='nostraight'

    return publicrank3type,publicsuit3type,publicstraight3type
 
def maxpublicrank3inhandrank(handsrank,publicrank):#2+3情况最大的对
    allrank=[]
    allrank.append(handsrank[0])
    allrank.append(handsrank[1])
    allrank.append(publicrank[0])
    allrank.append(publicrank[1])
    allrank.append(publicrank[2])
    a=0
    if kind(2,allrank)==max(publicrank):
        a=kind(2,allrank)
    return a

def pubilcsuit3inhandsuit(handssuit,suitpu,handsrank):#判断2+3时候四色同花自己的大小
    a=0
    handssuit.sort(reverse=True)
    handsrank.sort(reverse=True)
    for i in range(2):
        if handssuit[i]==suitpu:
            a=handsrank[i]
    return a

def straight3all(handsrank,publicrank):#判断2+3情况下是不是有顺子（4/5）
    typeallrank=0
    allrank=[]
    allrank.append(handsrank[0])
    allrank.append(handsrank[1])
    allrank.append(publicrank[0])
    allrank.append(publicrank[1])
    allrank.append(publicrank[2])
    allrank.sort(reverse=True)
    if ((allrank[0]-allrank[4]==4) or (allrank[0]==14 and allrank[1]-allrank[4]==3 and allrank[4]==2)) and len(set(allrank))==5:
        typeallrank=5
    else:
        for i in range(2,14):
            allp=allrank
            allp.append(i)
            allp.sort(reverse=True)
            if (allrank[0]-allrank[4]==4 and len(set(allrank[0:5]))==5) or (allrank[0]==14 and allrank[2]-allrank[5]==3 and allrank[5]==2 and len(set(allrank[2:6]))==4) or (allrank[0]==14 and allrank[1]-allrank[5]==3 and allrank[5]==2 and len(set(allrank[1:6]))==4):
                typeallrank=4
            if allrank[1]-allrank[5]==4 and len(set(allrank[1:6]))==5:
                typeallrank=4
    return typeallrank

def mixactionother(bet,bet1,bet2,publicbet):#选择动作，通过三个的bet
    betf=max(bet,bet1,bet2)
    if betf==0:
        a=random.random()
        if a>0.988:
            betf=publicbet
        
    return betf

def yourhand3max(hands,publichands):#判断你现在是最大的 手牌
    handsrank=[]
    publicrank=[]
    handssuit=[]
    publicsuit=[]
    for i in range(2):
        handsrank.append(hands[i][0])
        handssuit.append(hands[i][1])
    for i in range(3):
        publicrank.append(publichands[i][0])
        publicsuit.append(publichands[i][1])
    allrank=[]
    allrank.append(handsrank[0])
    allrank.append(handsrank[1])
    allrank.append(publicrank[0])
    allrank.append(publicrank[1])
    allrank.append(publicrank[2])
    allrank.sort(reverse=True)
    
    allsuit=[]
    allsuit.append(handssuit[0])
    allsuit.append(handssuit[1])
    allsuit.append(publicsuit[0])
    allsuit.append(publicsuit[1])
    allsuit.append(publicsuit[2])
    allsuit.sort(reverse=True)
    ranktype=0
    if ((allrank[0]-allrank[4]==4) or (allrank[0]==14 and allrank[1]-allrank[4]==3 and allrank[4]==2)) and len(set(allrank))==5:
        ranktype=4#顺子
        if len(set(allsuit))==1:
            ranktype=8#同花顺

    elif kind(4,allrank):
        ranktype=7
    elif kind(3, allrank) and kind(2, allrank):
        ranktype=6
    elif len(set(allsuit))==1 and ranktype==0:
        ranktype=5
    elif kind(3, allrank):
        ranktype=3
    elif kind(2,allrank):
        p=kind(2,allrank)
        allrank.remove(p)
        allrank.remove(p)
        if kind(2,allrank):
            ranktype=2
        else:
            ranktype=1
    else:
        ranktype=0
    return ranktype

def straight(rank1):
    ranks=rank1
    length=len(ranks)-4
    for i in range(length):
        rank=[]
        rank.append(ranks[i])
        rank.append(ranks[i+1])
        rank.append(ranks[i+2])
        rank.append(ranks[i+3])
        rank.append(ranks[i+4])
        if ((rank[0] - rank[4]) == 4 and len(set(rank)) == 5) or (rank[0]==14 and (rank[1] - rank[4]) == 3 and len(set(rank)) == 5):
            return rank[0]    


def two_pair(rank,ranks):
  pair=kind(2,ranks)
  lowpair = kind(2, rank)
  if pair != lowpair:
    return (lowpair, pair)
  else:
    return None

def flush(hand,ranks):
    flus=[]
    if  (kind(5,hand) or kind(6,hand) or kind(7,hand)):
        for i in [5,6,7]:
            if kind(i,hand):
                for ii in range(len(hand)):
                    if hand[ii]==kind(i,hand):
                        flus.append(ranks[ii])
    flus.sort(reverse=True)
    return flus 

def hand_rank(e):
    ranks=[]
    hand=[]
    rank=[]
    rank1=[]
    for i in range(len(e)):
        ranks.append(e[i][0])
        rank.append(e[i][0])
        hand.append(e[i][1])
        rank1.append(e[i][0])
    ranks.sort()
    rank.sort(reverse=True)
    rank1.sort(reverse=True)
    if kind(2,rank1):
        rank1.remove(kind(2,rank1))
    if kind(2,rank1):
        rank1.remove(kind(2,rank1))
    if kind(3,rank1):
        rank1.remove(kind(3,rank1))
        rank1.remove(kind(2,rank1))
    if flush(hand,ranks):
       a=flush(hand,ranks)
       a.sort(reverse=True)
       if straight(a):
           
           return (8,[straight(a)])
       else:
           
           return(5,[a[0],a[1],a[2],a[3],a[4]])
    
    elif kind(4, rank):
        
        p=kind(4,rank)
        rank.remove(p)
        rank.remove(p)
        rank.remove(p)
        rank.remove(p)
        return (7, [p, rank[0]])
    
    elif (kind(3, rank) and kind(2, rank)) or (kind(3, rank) and kind(3, ranks) and kind(3,rank)!=kind(3,ranks)):
        
        p=kind(3,rank)
        rank.remove(p)
        rank.remove(p)
        rank.remove(p)
        if kind(3,rank):
            return (6, [p, kind(3, rank)])
        else:
            return (6, [p, kind(2, rank)])
        
    elif straight(rank1):
        
        return (4, [straight(rank1)])
    
    elif kind(3, rank):
        
        p=kind(3,rank)
        rank.remove(p)
        rank.remove(p)
        rank.remove(p)
        return (3, [p, rank[0],rank[1]])
    
    elif two_pair(rank,ranks):
        #print(rank,ranks)
        p=kind(2,rank)
        q=kind(2,ranks)
        rank.remove(p)
        rank.remove(p)
        rank.remove(q)
        rank.remove(q)
        return (2, [p,q,rank[0]])
    
    elif kind(2, rank):
        p=kind(2, rank)
        rank.remove(p)
        rank.remove(p)
        return (1, [p, rank[0],rank[1],rank[2]])

    else:
        return (0, [rank[0],rank[1],rank[2],rank[3],rank[4]])

def run2_1otherblind(hands,publichands,publicbet):#2.1大盲位首先动作
    a=random.random()
    handsrank=[]
    publicrank=[]
    handssuit=[]
    publicsuit=[]
    allrank=[]
    allsuit=[]
    bet=0
    rank=0
    rank1=0
    rank2=0
    for i in range(2):
        handsrank.append(hands[i][0])
        handssuit.append(hands[i][1])
        allrank.append(hands[i][0])
        allsuit.append(hands[i][1])
    for i in range(3):
        publicrank.append(publichands[i][0])
        publicsuit.append(publichands[i][1])
        allrank.append(publichands[i][0])
        allsuit.append(publichands[i][1])
    #print(kind(3,publicsuit))
    publicrank3type,publicsuit3type,publicstraight3type=judgepublic3hand(publicrank,publicsuit)#public3type 存在三条，两条，什么都没有；三色同花，两色同花，什么都没有；一个顺子，一个类顺子
    if publicrank3type=='three kill':
        if kind(4,allrank):##有一个牌组成了四条，公共牌三条
            action='raise'
            bet=publicbet
            rank=8 #max you can get
        else:
            if max(handsrank)>=13:
                action='raise'
                bet=100
            else:
                action='call'
                bet=0
    elif publicrank3type=='one pair':
        if handinpubliconepair3(handsrank,publicrank)==1:#即公共牌三张有一对，我们抽成了一个三条/四条
            if kind(2,handsrank):
                rank=8#4条
                action='raise'
                bet=publicbet
            elif kind(2,allrank) and kind(3,allrank):#(3+2)的葫芦
                rank=7#葫芦
                action='raise'
                bet=publicbet
            else:
                rank=3
                action='raise'
                bet=publicbet
        else:
            if kind(2,handsrank) and kind(2,handsrank)>11:
                rank=1.9
                action='raise'
                bet=publicbet
            elif kind(2,handsrank) and kind(2,handsrank)<10:
                action='raise'
                bet=publicbet/2
                rank=1.7
            else:
                if max(handsrank)>12:
                    action='raise'
                    bet=100
                    rank=0.5
                else:
                    action='call'
                    bet=0
                    rank=0
    else:    
        if kind(2,allrank) and kind(2,allrank)==max(publicrank):#公共牌什么都没有情况下自己手牌是最大对
            action='raise'
            bet=publicbet
            rank=1.6

        elif kind(2,allrank) and (kind(2,allrank)<max(publicrank) and kind(2,allrank)>min(publicrank)):#不是最大对
            rank=1.3
            if a<0.021:
                action='raise'
                bet=publicbet/2
            else:
                action='raise'
                bet=100

        else:#最小的对
            rank=1.2
            if a<0.031:
                action='raise'
                if publicbet<=600:
                    bet=100
            else:
                action='call'
                bet=0
                rank=1.1


    if publicsuit3type=='threesuits':
        if kind(5,allsuit):
            print('you have flash in  3 hands')
            rank1=6
            action1='raise'
            bet1=publicbet
            if max(handsrank)>11:
                rank1=6.5
            else:
                rank1=6.1

        elif kind(4,allsuit):
            if (handssuit[0]==kind(3,publicsuit) and handsrank[0]>11) or (handssuit[1]==kind(3,publicsuit) and handsrank[1]>11):
                rank1=5.4#现在为止 有7/16的概率为同花，且很大
                action1='raise'
                bet1=publicbet
            elif (handssuit[0]==kind(3,publicsuit) and handsrank[0]<12 and handsrank[0]>7) or (handssuit[1]==kind(3,publicsuit) and handsrank[1]<12 and handsrank[1]>7):
                rank1=5.3
                action1='raise'
                bet1=publicbet

            else:
                rank1=5.2
                if a<0.023:
                    action1='call'
                    bet1=0
                else:
                    action1='raise'
                    bet1=publicbet/2
        else:
            action1='call'
            bet1=0

    elif publicsuit3type=='twosuits':
        if kind(4,handssuit):#即公共牌三张有一对，我们抽成了一个三条/四条
            if max(handsrank)>11:
                rank1=5.9
                action1='raise'
                bet1=publicbet*3


            elif max(handsrank)<8:
                rank1=5.7
                action1='raise'
                bet1=publicbet*2
            else:
                rank1=5.8
                action1='raise'
                bet1=publicbet
        else:
            action1='call'
            bet1=0
    else:
        action1='call'
        bet1=0

    if publicstraight3type=='3threestraight':
        if straight3all(handsrank,publicrank)==5:#现在已经成了顺子
            print('you have straight in 3 hands')
            rank2=5
            action2='raise'
            bet2=publicbet
        elif straight3all(handsrank,publicrank)==4:
            action2='call'#2/13或者4/13的概率成顺子
            bet2=0
            rank2=4.4
        else:
            action2='call'
            bet2=0
    elif publicstraight3type=='nostraight' and straight3all(handsrank,publicrank)==4:#即2个自己的牌和公共牌组成了4张顺或者差一张为顺
        rank2=4.9
        action2='raise'
        bet2=publicbet*0.5
    else:
        bet2=0
        action2='call'
    #print(bet,bet1,bet2)
    betf=mixactionother(bet,bet1,bet2,publicbet)
    if betf==0:
        actionf='call'
    else:
        actionf='raise'
    return actionf,betf,[rank,rank1,rank2]
         
def run2elseblind(hands,publichands,opobet,publicbetbefore):#2.1小盲位的动作
    a=random.random()
    handsrank=[]
    publicrank=[]
    handssuit=[]
    publicsuit=[]
    allrank=[]
    allsuit=[]
    for i in range(2):
        handsrank.append(hands[i][0])
        handssuit.append(hands[i][1])
        allrank.append(hands[i][0])
        allsuit.append(hands[i][1])
    for i in range(3):
        publicrank.append(publichands[i][0])
        publicsuit.append(publichands[i][1])
    publicrank3type,publicsuit3type,publicstraight3type=judgepublic3hand(publicrank,publicsuit)#public3type 存在三条，两条，什么都没有；三色同花，两色同花，什么都没有；一个顺子，一个类顺子
    action,bet,ranktype=run2_1otherblind(hands,publichands,publicbetbefore)
    if opobet==0:#对面call牌        
        actionf=action
        betf=bet
    elif opobet>0 and opobet<=publicbetbefore :
        if bet==opobet:
            actionf='call'
            betf=bet
        elif bet>opobet:
            actionf='raise'
            betf=-publicbetbefore/2+3*opobet#publicbet
        else:
            actionf='fold'
            betf=0
    elif opobet>0 and opobet>=publicbetbefore  and opobet<=3000:
        if bet==opobet:
            if sum(ranktype)>8:
                actionf='raise'
                betf=3*opobet
            else:
                actionf='call'
                betf=0
            
        elif bet<opobet and bet>0:
            if sum(ranktype)>6:
                actionf='raise'
                betf=3*opobet
            else:
                actionf='call'
                betf=0
        else:
            actionf='fold'
            betf=0
    else:
        if opobet>3000:
            if (ranktype[1]==6) or (ranktype[2]==5) :

                actionf='allin'
                betf=20000
#            else:
#                if a<0.9822:
#                    actionf='fold'
#                    betf=0
#                else:
#                    actionf='call'
#                    betf=0
#        else:
            if ranktype[0]>=1.5 or (ranktype[1]>4.9) or (ranktype[2]==5):
                actionf='raise'
                betf=3*opobet
            else:
                actionf='fold'
                betf=0

    return actionf,betf


 
def kind2(n, ranks):#判断有几张是一样的
  for s in ranks:
    if ranks.count(s) == n : return s
  return None#           
def run3_1otherblind(hands,publichands,publicbet):##提示动作，我们
    handsrank=[]
    publicrank=[]
    handssuit=[]
    publicsuit=[]
    allrank=[]
    allsuit=[]
    for i in range(2):
        handsrank.append(hands[i][0])
        handssuit.append(hands[i][1])
        allrank.append(hands[i][0])
        allsuit.append(hands[i][1])
    for i in range(4):
        publicrank.append(publichands[i][0])
        publicsuit.append(publichands[i][1])
        allrank.append(publichands[i][0])
        allsuit.append(publichands[i][1])

    allhands=[]
    allhands.append(hands[0])
    allhands.append(hands[1])
    allhands.append(publichands[0])
    allhands.append(publichands[1])
    allhands.append(publichands[2])
    allhands.append(publichands[3])
    #print(publicsuit)
    #print(kind(4,publicsuit))
    if len(allsuit)==6:
        handtype,maxhandfeature=hand_rank(allhands)
        rank=handtype
        #print(yourhand3max(hands,publichands[0:3]),handtype)
        if handtype==yourhand3max(hands,publichands[0:3]):
            if handtype==0:#仅仅是平牌，没有什么本质性的变化
                action='call'
                bet=0
                rank=0
                if len(set(publicsuit))==1:
                    rank=-6#对手有很大可能是同花
#                    print(rank)
                else:
                    rank=0
                if kind(4,allsuit) and kind(2,publicsuit):
                    rank=1.8
                    action='raise'
                    bet=100
            elif handtype==1:
                if kind(2,publicrank):
                    rank=-1
                    action='call'
                    bet=0
                elif (max(publicrank)==handsrank[0] or max(publicrank)==handsrank[1]):#1对，最大的哪一个,且现在有1/4的概率是同花
                    if kind(2,handssuit) and kind(2,publicsuit) and kind(4,publicsuit):
                        action='raise'
                        bet=publicbet
                        if max(handsrank)>12:
                            rank=1.9
                        else:
                            rank=1.7
                    else:
                        action='raise'
                        bet=publicbet
                        rank=1.8
                else:
                    action='call'
                    bet=0
                    rank=1.3
            elif handtype==2:
                if (max(publicrank)==handsrank[0] or max(publicrank)==handsrank[1]) or (kind(2,handsrank) and kind(2,publicrank) and kind(2,handsrank)>kind(2,publicrank)):
                    action='raise'
                    bet=publicbet
                    rank=2.9
                else:
                    if kind(2,publicrank) and kind(2,publicrank)>max(handsrank):
                        c=kind(2,publicrank)
                        publicrank.remove(c)
                        publicrank.remove(c)
                        if max(handsrank)==max(publicrank):
                            action='raise'
                            bet=publicbet
                            rank=2.9
                        else:
                            action='raise'
                            rank=2.3
                            bet=publicbet
                    else:
                        action='call'
                        bet=0 
                        rank=0
                    if len(set(publicrank))==3:
                        rank=-1.5
                    if len(set(publicrank))==2:
                        rank=-2
            elif handtype==3 :
                if kind(3,publicrank):
                    action='call'
                    bet=0
                    rank=-3
                elif kind(2,publicrank):
                    action='raise'
                    bet=publicbet
                    rank=3.5
                else:
                    action='raise'
                    rank=3.8
                    bet=publicbet
            else:
                action='raise'
                rank=handtype
                bet=publicbet

        elif handtype-yourhand3max(hands,publichands[0:3])==1 and handtype==1:#长一个点，即从没-1 1-2
            if max(publicrank)==handsrank[0] or max(publicrank)==handsrank[1]:
                action='raise'
                bet=publicbet/2
                rank=1.9
            else:
                action='raise'
                bet=100
                
        elif handtype-yourhand3max(hands,publichands[0:3])==1 and handtype==2:
            #长一个点，即从没-1 1-2
            if publicrank[3]==handsrank[0] or publicrank[3]==handsrank[1]:
                if max(publicrank)==publicrank[3]:
                    action='raise'
                    bet=publicbet
                    rank=2.9
                else:
                    action='raise'
                    bet=100
                    rank=2.3
            else:
                action='raise'
                bet=100
                
        elif handtype-yourhand3max(hands,publichands[0:3])>=2:
            action='raise'
            bet=publicbet
            rank=handtype
        else:
            action='call'
            bet=0
    return action,bet,rank

def run3_1undergunblind(hands,publichands,opobet,publicbetbefore):#3.1小盲位的动作
    a=random.random()
    handsrank=[]
    publicrank=[]
    handssuit=[]
    publicsuit=[]
    allrank=[]
    allsuit=[]
    for i in range(2):
        handsrank.append(hands[i][0])
        handssuit.append(hands[i][1])
        allrank.append(hands[i][0])
        allsuit.append(hands[i][1])
        
    for i in range(4):
        publicrank.append(publichands[i][0])
        publicsuit.append(publichands[i][1])
        allrank.append(publichands[i][0])
        allsuit.append(publichands[i][1])

    allhands=[]
    allhands.append(hands[0])
    allhands.append(hands[1])
    allhands.append(publichands[0])
    allhands.append(publichands[1])
    allhands.append(publichands[2])
    allhands.append(publichands[3])
    handtype6,handfea6=hand_rank(allhands)
    action,bet,rank=run3_1otherblind(hands,publichands,publicbetbefore)
    if opobet==0:#对面call牌
        actionf=action
        betf=bet
    elif opobet==100:
        if bet==opobet:
            actionf='call'
            betf=bet
        elif bet>opobet:
            if bet==publicbetbefore/2:
                actionf='raise'
                betf=opobet*2-publicbetbefore/2
            else:
                actionf='raise'
                betf=opobet*3-publicbetbefore/2
                
        else:
            if max(handsrank)>11 or max(handsrank)>min(publicrank):
                actionf='call'
                betf=100
            else:
                actionf='fold'
                betf=0
    elif opobet>100 and opobet<=publicbetbefore/2 :
        if bet==opobet:
            actionf='call'
            betf=bet
        elif bet>opobet:
            actionf='raise'
            betf=opobet*3-publicbetbefore/2
        else:
            if (rank==2 or rank==2.3) and opobet<=400:
                actionf='call'
                betf=opobet
            else:
                actionf='fold'
                betf=0

    elif opobet>0 and opobet==publicbetbefore and opobet>publicbetbefore/2:
        if bet==opobet:
            if rank>=2.9:
                actionf='raise'
                bet=opobet*3-publicbetbefore/2
            else:
                actionf='call'
                betf=opobet
        else:
            if a>0.9421:
                actionf='raise'
                betf=opobet*3-publicbetbefore/2
            else:
                actionf='fold'
                betf=0
    elif opobet>publicbetbefore:       
        if rank>=2.9 or rank==1.8:
            actionf='raise'
            betf=opobet*3-publicbetbefore/2
        else:
            actionf='fold'
            betf=0
    else:
        actionf='fold'
        betf=0
   
    return actionf,betf

def run3elseblind(hands,publichands,opobet,publicbetbefore):#3.1小盲位的动作
    a=random.random()
    handsrank=[]
    publicrank=[]
    handssuit=[]
    publicsuit=[]
    allrank=[]
    allsuit=[]
    for i in range(2):
        handsrank.append(hands[i][0])
        handssuit.append(hands[i][1])
        allrank.append(hands[i][0])
        allsuit.append(hands[i][1])
        
    for i in range(4):
        publicrank.append(publichands[i][0])
        publicsuit.append(publichands[i][1])
        allrank.append(publichands[i][0])
        allsuit.append(publichands[i][1])

    allhands=[]
    allhands.append(hands[0])
    allhands.append(hands[1])
    allhands.append(publichands[0])
    allhands.append(publichands[1])
    allhands.append(publichands[2])
    allhands.append(publichands[3])
    handtype6,handfea6=hand_rank(allhands)
    action,bet,rank=run3_1otherblind(hands,publichands,publicbetbefore)
    if opobet==0:#对面call牌
        actionf=action
        betf=bet
    elif opobet==100:
        if bet==opobet:
            actionf='call'
            betf=bet
        elif bet>opobet:
            if bet==publicbetbefore/2:
                actionf='raise'
                betf=opobet*2-publicbetbefore/2
            else:
                actionf='raise'
                betf=opobet*3-publicbetbefore/2
        else:
            if max(handsrank)>11 or max(handsrank)>min(publicrank):
                actionf='call'
                betf=100
            else:
                actionf='fold'
                betf=0
    elif opobet>0 and opobet<=publicbetbefore/2:
        if bet==opobet:
            actionf='call'
            betf=bet
        elif bet>opobet:
            actionf='raise'
            betf=opobet*3-publicbetbefore/2
        else:
            if (rank==2 or rank==2.3) and opobet<=400:
                actionf='call'
                betf=opobet
            else:
                actionf='fold'
                betf=0

    elif opobet>0 and opobet<=2*publicbetbefore and opobet>publicbetbefore/2:
        if bet==opobet:
            if rank>=1.8:
                actionf='raise'
                bet=opobet*3-publicbetbefore/2
            else:
                actionf='call'
                betf=opobet
        else:
            if a>0.9421:
                actionf='raise'
                betf=opobet*3-publicbetbefore/2
            else:
                actionf='fold'
                betf=0
    elif opobet>2*publicbetbefore:
        if rank>=2.9:
            actionf='raise'
            betf=opobet*3-publicbetbefore/2
        else:
            actionf='fold'
            betf=0
    else:
        actionf='fold'
        betf=0
   
    return actionf,betf

def run4_1otherblind(hands,publichands,publicbet):#4.1大盲位动作
    a=random.random()
    handsrank=[]
    publicrank=[]
    handssuit=[]
    publicsuit=[]   
    for i in range(2):
        handsrank.append(hands[i][0])
        handssuit.append(hands[i][1])
    for i in range(5):
        publicrank.append(publichands[i][0])
        publicsuit.append(publichands[i][1])

    allhands=[]
    allhands.append(hands[0])
    allhands.append(hands[1])
    allhands.append(publichands[0])
    allhands.append(publichands[1])
    allhands.append(publichands[2])
    allhands.append(publichands[3])
    allhands.append(publichands[4])
    action='call'
    bet=0
    handtype7,maxhandfeature7=hand_rank(allhands)
    handtype6,maxhandfeature6=hand_rank(allhands[0:6])
    if yourhand3max(publichands[0:2],publichands[2:5])==0:#整个公共牌-0 公共牌什么都没有
        if handtype7==handtype6:
            if handtype7==0:#仅仅是平牌，没有什么本质性的变化
                if max(handsrank)>11:
                    if a>0.9632:
                        action='raise'
                        bet=100
                    else:
                        action='call'
                        bet=0
                else:
                    action='call'
                    bet=0
            if handtype7==1:
                if max(publicrank)==max(handsrank) or max(publicrank)==min(handsrank):
                    if a<0.92669 :
                        action='raise'
                        bet=publicbet/2
                        if bet<400:
                            bet=publicbet
                    else:
                        action='call'
                        bet=0
                else:
                    action='call'
                    bet=0
            elif handtype7==2:
                if max(publicrank)==max(handsrank) or max(publicrank)==min(handsrank):
                    if a<0.95102:
                        action='raise'
                        bet=publicbet
                    else:
                        action='raise'
                        bet=publicbet/2
                else:
                    action='call'
                    bet=0
            elif handtype7<5 and handtype7>2:
                if len(set(publicsuit))==4 :#必要的实验，看看对面是不是同花
                    action='raise'
                    bet=100
                else:
                    if a>0.9225:
                        action='call'
                        bet=0
                    else:
                        action='raise'
                        bet=publicbet
            else:
                if a>0.9955:
                    action='call'
                    bet=0
                elif a<0.9955 and a>0.0322:
                    action='raise'
                    bet=publicbet
                else:
                    action='raise'
                    bet=publicbet/2
        elif handtype7-handtype6==1:#长一个点，即从没-1 1-2
            if a>0.98848:
                action='call'
                bet=0
            else:
                action='raise'
                bet=publicbet/2
    else:
        if handtype7>yourhand3max(publichands[0:2],publichands[2:5]):
            if handtype7<=1:
                action='call'
                bet=0
            elif handtype7==2:
                if max(publicrank)==max(handsrank):
                    if a>0.81102:
                        action='raise'
                        bet=100
                    else:
                        action='raise'
                        bet=publicbet/2
            elif handtype7<5 and handtype7>2:
                if len(set(publicsuit))==4 :#必要的实验，看看对面是不是同花
                    action='raise'
                    bet=100
                else:
                    if a>0.9225:
                        action='call'
                        bet=0
                    else:
                        action='raise'
                        bet=publicbet/2
            else:
                if a<0.995:
                    action='raise'
                    bet=publicbet
                else:
                    action='raise'
                    bet=publicbet/2
        else:
            action='call'
            bet=0
            
    return action,bet

def run4_elseblind(hands,publichands,opobet,publicbetbefore):#3.1小盲位的动作
    a=random.random()
    handsrank=[]
    publicrank=[]
    handssuit=[]
    publicsuit=[]
    for i in range(2):
        handsrank.append(hands[i][0])
        handssuit.append(hands[i][1])
    for i in range(5):
        publicrank.append(publichands[i][0])
        publicsuit.append(publichands[i][1])

    allhands=[]
    allhands.append(hands[0])
    allhands.append(hands[1])
    allhands.append(publichands[0])
    allhands.append(publichands[1])
    allhands.append(publichands[2])
    allhands.append(publichands[3])
    allhands.append(publichands[4])
    handtype7,feahand7=hand_rank(allhands)
    action,bet=run4_1otherblind(hands,publichands,publicbetbefore)
    actionf=action
    betf=bet
    if opobet==0:#对面call牌
        actionf=action
        betf=bet
    elif opobet>0 and opobet<=publicbetbefore/2 :
        if bet==opobet:
            actionf='call'
            betf=bet
        elif bet>opobet:
            actionf='raise'
            betf=opobet*3-publicbetbefore/2
        else:
            if a>0.98611:
                actionf='call'
                betf=opobet
            else:
                actionf='fold'
                betf=0
    elif opobet>0 and opobet>publicbetbefore/2  and opobet<=publicbetbefore*1.5:
        if bet==opobet:
            actionf='call'
            betf=bet
        elif bet>opobet:
            actionf='raise'
            betf=opobet*3-publicbetbefore/2
        else:
            actionf='fold'
            betf=0
    else:
        actionf='fold'
        betf=0
    if opobet>3*publicbetbefore or opobet>5000:
        if handtype7==2 or handtype7==3:
            if kind(4,publicsuit):

                action='fold'
                betf=0
            else:
                actionf='call'
                betf=opobet
                if opobet>=3000 and (max(handsrank)==max(publicrank) or  kind(2,handsrank)) :
                    if kind(3,publicsuit) or kind(2,publicsuit):
                        actionf='call'
                        betf=opobet
                    else:
                        action='fold'
                        betf=0

        elif handtype7==4:
            if ((max(feahand7)==handsrank[0] or max(feahand7)==handsrank[1]) and straight3all(publicrank[0:2],publicrank[2:5])<5) or (straight3all(publicrank[0:2],publicrank[2:5])==4):
                if kind(4,publicsuit):
                    action='call'
                    betf=0
                else:
                    action='raise'
                    betf=min(opobet*3,20000-publicbetbefore/2)
            else:
                if a>0.1288:
                    actionf='call'
                    betf=bet
                elif a<0.9244 and a>0.1288:
                    actionf='raise'
                    betf=min(opobet*2,20000-publicbetbefore/2)
                else:
                    actionf='raise'
                    betf=min(opobet*3,20000-publicbetbefore/2)
        elif handtype7==5:
            if (kind(4,publicrank) and handsrank[0]>11 and handssuit[0]==kind(4,publicrank)) or (kind(4,publicrank) and handsrank[1]>11 and handssuit[1]==kind(4,publicrank)) or kind(3,publicrank):
                if a>0.0888:
                    actionf='call'
                    betf=bet
                elif a<0.9744 and a>0.0888:
                    actionf='raise'
                    betf=min(opobet*3,20000-publicbetbefore/2)
                else:
                    actionf='raise'
                    betf=min(opobet*2,20000-publicbetbefore/2)                
            
        elif yourhand3max(hands,publichands)>5:
            if a>0.0155:
                actionf='call'
                betf=opobet
            else:
                actionf='raise'
                betf=min(opobet*3,20000-publicbetbefore/2)
        else:
            actionf='fold'
            betf=0
    
    
    return actionf,betf

def turnhandrank(hand):
    a=0
    if hand=='A':
        a=14
    elif hand=='K':
        a=13
    elif hand=='Q':
        a=12
    elif hand=='J':
        a=11
    elif hand=='T':
        a=10
    elif hand=='9':
        a=9
    elif hand=='8':
        a=8
    elif hand=='7':
        a=7
    elif hand=='6':
        a=6
    elif hand=='5':
        a=5
    elif hand=='4':
        a=4
    elif hand=='3':
        a=3
    elif hand=='2':
        a=2
    return a

def turnhandsuit(hand):
    a=0
    if hand=='c':
        a=1
    elif hand=='d':
        a=2
    elif hand=='s':
        a=3

    else:
        a=4
    return a

def handt(hand):
    return hand


def handt2(hand,board):
    b=int(len(board))
    hand1=np.zeros((int(2+b),2))
    hand1[0:2,:]=hand
    hand1[2:int(2+b),:]=board

    return hand1
        

def changeonecard(a):
	hand=np.zeros(2)
	if a[0]=="A":
		hand[0]=14
	elif a[0]=="K":
		hand[0]=13
	elif a[0]=="Q":
		hand[0]=12
	elif a[0]=="J":
		hand[0]=11
	elif a[0]=="T":
		hand[0]=10
	else:
		hand[0]=int(a[0])
	if a[1]=="c":
		hand[1]=1
	elif a[1]=="h":
		hand[1]=2
	elif a[1]=="s":
		hand[1]=3
	elif a[1]=="d":
		hand[1]=4
	return hand


def changeprivate_card(inputinfo):
	hand=np.zeros((2,2))
	a=inputinfo["private_card"]
	for i in range(2):
		hand[i][:]=changeonecard(a[i])
	return hand

def changepublic_card(inputinfo):
	
	a=inputinfo["public_card"]
	lena=len(a)
	hand=np.zeros((lena,2))
	for i in range(lena):
		hand[i][:]=changeonecard(a[i])
	return hand



def getopobet(inputinfo):
    pos=inputinfo["action_position"]
    lena=len(inputinfo["action_history"])
    infothisturn=inputinfo["action_history"][lena-1]
    if infothisturn==[]:
        infothisturn=inputinfo["action_history"][lena-2]
    opt_bet=0
    lenaa=len(infothisturn)
    for i in range(lenaa):
        bet=infothisturn[i]["action"]
        pos1=infothisturn[i]["position"]
        if bet[0]=="r" and (int(pos)>int(pos1) or int(pos)<int(pos1)):
            opt_bet=int(bet[1:len(bet)])
    return opt_bet




def humix(action,bet,allinbet):
    if action=='r0' or (action=='raise' and bet==0):
        plac='call'
        action='call'
    if action=='call' or action=='check':
        plac='call'
    elif action=='fold':
        plac='fold'
    else:
        if bet==0:
            bet=300
        bet=int(bet)
        if bet<allinbet:
            plac='r'+str(bet)
        else:
            plac='r'+str(allinbet)
    if plac=='r0':
        plac='call'
    return plac

def getbotbet(inputinfo):
    pos=inputinfo["action_position"]
    lena=len(inputinfo["action_history"])
    infothisturn=inputinfo["action_history"][lena-1]
    if infothisturn==[]:
        infothisturn=inputinfo["action_history"][lena-2]
    bot_bet=0
    lenaa=len(infothisturn)
    for i in range(lenaa):
        bet=infothisturn[i]["action"]
        pos1=infothisturn[i]["position"]
        if bet[0]=="r" and int(pos)==int(pos1):
            bot_bet=int(bet[1:len(bet)])
    return bot_bet

def getbet1(inputinfo):
    playerinfo=inputinfo["players"]
    allplayersbet=np.zeros(int(len(playerinfo)))

    for i in range(int(len(playerinfo))):
        allplayersbet[i]=20000-int(playerinfo[i]["money_left"])
        
    pos1=inputinfo["position"]
    bot_bet=allplayersbet[pos1]
    allplayersbet[pos1]=0
    opobet=max(allplayersbet)
    return bot_bet,opobet


        
def getallin(inputinfo):
    bet=inputinfo['raise_range']
   
    if bet==[]:
        maxbet=0
    else:
        maxbet=bet[1]
    return maxbet
    
def allturnundergunblindaction(inputinfo):
    hand=changeprivate_card(inputinfo)
    board=changepublic_card(inputinfo)	
#    bot_bet=getbotbet(inputinfo)
#    opobet=getopobet(inputinfo)
    allinbet=getallin(inputinfo)
    bot_bet,opobet=getbet1(inputinfo)
    a=len(board)
    if a==0:
        if bot_bet==0:
            advice,amount=run1_1undergunblind(handt(hand),opobet)
        elif bot_bet>0:
            advice,amount=run1_2undergunblind(handt(hand),opobet,bot_bet)

    elif  a==3:
        if bot_bet==0:
            advice,amount=run2elseblind(handt(hand),handt(board),opobet,bot_bet*2)
        else:
            advice,amount=run2elseblind(handt(hand),handt(board),opobet,bot_bet*2)
    elif a==4:
        if bot_bet==0:
            advice,amount=run3_1undergunblind(handt(hand),handt(board),opobet,bot_bet*2)
        elif bot_bet>0:
            advice,amount=run3elseblind(handt(hand),handt(board),opobet,bot_bet*2)
        else:
            advice='call'
    else:
        if bot_bet==0:
            advice,amount=run4_elseblind(handt(hand),handt(board),opobet,bot_bet*2)
        elif bot_bet>0:
            advice,amount=run4_elseblind(handt(hand),handt(board),opobet,bot_bet*2)
        else:
            if handsrank1(handt2(hand,board))>5:
                advice='raise'
                amount=getallin(inputinfo)
            else:
                advice='fold'
    
    return humix(advice,amount,allinbet)


def allturnotherblindaction(inputinfo):
    hand=changeprivate_card(inputinfo)
    board=changepublic_card(inputinfo)
#    bot_bet=getbotbet(inputinfo)#自己这一个阶段上一次bet值
#    opobet=getopobet(inputinfo)#对面所有人该阶段bet的最大值
    bot_bet,opobet=getbet1(inputinfo)
    allinbet=getallin(inputinfo)
    a=len(board)
    if a==0:
        if bot_bet<=50:
            advice,amount=run1_1otherblind(handt(hand),opobet)
        else:
            advice,amount=run1_2otherblind(handt(hand),opobet,bot_bet)
    elif a==3:
        if bot_bet==0:
            advice,amount,rankty=run2_1otherblind(handt(hand),handt(board),bot_bet*2)
        elif bot_bet>0:
            advice,amount=run2elseblind(handt(hand),handt(board),opobet,bot_bet*2)
        else:
            c=max(handt(board)[0][0],handt(board)[1][0],handt(board)[2][0])
            if opobet<max(bot_bet*2,800) and opobet>=max(bot_bet,300):
                if (yourhand3max(handt(hand),handt(board))>2 or (c==handt(hand)[0][0] or c==handt(hand)[1][0])):
                    advice='raise'
                    amount=max(bot_bet*2,2000)
                else:
                    advice='fold'
                    amount=0
            elif opobet>=max(bot_bet*2,800):
                if (yourhand3max(handt(hand),handt(board))>2 or (c==handt(hand)[0][0] or c==handt(hand)[1][0])):
                    advice='raise'
                    amount=max(bot_bet,800)+opobet
                else:
                    advice='fold'
                    amount=0
            else:
                advice='call'
                amount=opobet
    elif  a==4:
        if bot_bet==0:
            advice,amount,rankty=run3_1otherblind(handt(hand),handt(board),bot_bet*2)
        elif bot_bet>0:
            advice,amount=run3elseblind(handt(hand),handt(board),opobet,bot_bet*2)
        else:
            advice='call'
    else:
        if bot_bet==0:
            advice,amount=run4_1otherblind(handt(hand),handt(board),bot_bet*2)
        elif bot_bet>0:
            advice,amount=run4_elseblind(handt(hand),handt(board),opobet,bot_bet*2)
        else:
            if handsrank1(handt2(hand,board))>5:
                advice='raise'
                amount=allinbet
            else:
                advice='fold'
    
    return humix(advice,amount,allinbet)

def getsixbotaction(inputinfo):
	pos=inputinfo['action_position']
	if pos==2 or pos==3 or pos==4 or pos==5 or pos==0:
		actionbet=allturnundergunblindaction(inputinfo)
	else:
		actionbet=allturnotherblindaction(inputinfo)
	return actionbet

def get_action(data,betaction):
    if 'check' in data['legal_actions'] and betaction=='call':
        action = 'check'
    else:
        action=betaction

    return action

def sendJson(request, jsonData):
    data = json.dumps(jsonData).encode()
    request.send(struct.pack('i', len(data)))
    request.sendall(data)


def recvJson(request):
    data = request.recv(4)
    length = struct.unpack('i', data)[0]
    data = request.recv(length).decode()
    while len(data) != length:
        data = data + request.recv(length - len(data)).decode()
    data = json.loads(data)
    return data


class RuleAgent6p(Agent):
    
    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.server, self.port))
        try:
            sendJson(client, self.info)
            while True:
                data = recvJson(client)
                if data['info'] == 'state':
                    position = data['position']
                    if data['position'] == data['action_position']:
                        betaction = getsixbotaction(data)
                        action = get_action(data,betaction)
                        sendJson(client, {'action': action, 'info': 'action'})
                        privatecard=data['private_card']
                elif data['info'] == 'result':
                    # print("position",position)
                    print('win money: {},\tyour card: {},\topp card: {},\t\tpublic card: {}'.format(
                        data['players'][position]['win_money'], privatecard, data['player_card'], data['public_card'])) 
                    sendJson(client, {'info': 'ready', 'status': 'start'})
                else:
                    break
        except Exception as e:
            traceback.print_exc()
        finally:
            client.close()


if __name__ == "__main__":
    agent = RuleAgent6p(1000006, 6, "Test", 100, "holdem.ia.ac.cn", 18888, ["HotheadManiac", "ScaredLimper", "CandidStatistician", "RandomGambler", "LooseAggressive"], verbose=True)
    agent.run()