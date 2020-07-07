#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <iostream>
#include "CJsonObject.hpp"
#include "cJSON.h"
#include <vector>
#include <string>
#include <netdb.h>
using namespace std;

typedef neb::CJsonObject json;
#define server_host  "holdem.ia.ac.cn"
#define server_port  18888

/*
    根据游戏的状态信息，返回对应的动作。

    Args:
        data: json 表示游戏的状态

    Return:
        action: string 表示制定的动作
*/
string get_action(json data)
{
    string action;
    int check = 0;
    for (int i = 0; i < data["legal_actions"].GetArraySize(); ++i)
    {
        string action;
        data["legal_actions"].Get(i, action);
        if (action == "check")
            check = 1;
    }
    if (check) action = "check"; else action = "call";
    return action;
}
int connectServer()
{
    struct hostent *ht = gethostbyname(server_host);
    char *server_ip =  inet_ntoa(*((struct in_addr *)ht->h_addr_list[0]));
    int sock_cli = socket(AF_INET,SOCK_STREAM, 0);
    struct sockaddr_in servaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(server_port);
    servaddr.sin_addr.s_addr = inet_addr(server_ip);
    if (connect(sock_cli, (struct sockaddr *)&servaddr, sizeof(servaddr)) < 0)
    {
        perror("connect error");
        exit(1);
    }
    return sock_cli;
}

char sendbuf[100000];
char recvbuf[100000];
void sendLength(int socket, int dataLength)
{
    memset(sendbuf, 0, sizeof(sendbuf));
    for (int i = 0; i < 4; ++i)
    {
        unsigned char x = dataLength % 256;
        dataLength /= 256;
        sendbuf[i] = x;
    }
    send(socket, sendbuf, 4, 0);
}
int recvLength(int socket)
{
    memset(recvbuf, 0, sizeof(recvbuf));
    recv(socket, recvbuf, 4, 0);
    int ans = 0;
    for (int i = 3; i >= 0; --i)
    {
        unsigned char x = recvbuf[i];
        ans = ans * 256 + x;
    }
    return ans;
}
void sendMessage(int socket, string message)
{
    int dataLength = strlen(message.c_str());
    sendLength(socket, dataLength);
    memset(sendbuf, 0, sizeof(sendbuf));
    strcpy(sendbuf, message.c_str());
    send(socket, sendbuf, strlen(sendbuf), 0);
}
json receiveMessage(int socket)
{
    int dataLength = recvLength(socket);;
    memset(recvbuf, 0, sizeof(recvbuf));
    recv(socket, recvbuf, dataLength, 0);
    return json(recvbuf);
}
string actionMessage(string action)
{
    json message;
    message.Add("info", "action");
    message.Add("action", action);
    return message.ToString();
}
string connectMessage(int room_id, int room_number, string name, int game_number, vector <string> bots)
{
    json message;
    message.Add("info", "connect");
    message.Add("room_id", room_id);
    message.Add("name", name);
    message.Add("game_number", game_number);
    message.Add("room_number", room_number);
    message.AddEmptySubArray("bots");
    for (int i = 0; i < (int)bots.size(); ++i)
    {
        message["bots"].Add(bots[i]);
    }
    return message.ToString();
}
string startMessage()
{
    json message;
    message.Add("info", "ready");
    message.Add("status", "start");
    return message.ToString();
}

void run(int socket, int room_id, int room_number, string name, int game_number, vector<string> bots)
{
    json message;
    sendMessage(socket, connectMessage(room_id, room_number, name, game_number, bots));
    int position;
    while (true)
    {
        message = receiveMessage(socket);
        if (message("info") == "state" ) 
        {
            if (message("position") == message("action_position"))
            {
                position =  atoi(message("position").c_str());
                int check = 0;
                for (int i = 0; i < message["legal_actions"].GetArraySize(); ++i)
                {
                    string action;
                    message["legal_actions"].Get(i, action); 
                    if (action == "check")
                        check = 1;
                }
                if (check)  sendMessage(socket, actionMessage("check"));
                else  sendMessage(socket, actionMessage("call"));
            }
        }
        else if (message("info") == "result")
        {   
            string win_money = message["players"][position]["win_money"].ToFormattedString();
            string your_card = message["player_card"][position].ToFormattedString();
            string opp_card = message["player_card"][1 - position].ToFormattedString();
            string public_card = message["public_card"].ToFormattedString();
            cout << "win_money: " << win_money << " ";
            cout << "your_card: " << your_card << " ";
            cout << "opp_card: " << opp_card << " ";
            cout << "public_card: " << public_card << " ";
            cout << endl;
            sendMessage(socket, startMessage());
        }
        else 
        {
            cout << message.ToFormattedString() << endl;
            break;
        }
    }
}
int main(int argc, char *argv[])
{
    int room_id = atoi(argv[1]);             // 进行对战的房间号
    int room_number = atoi(argv[2]);         // 一局游戏人数
    string name = argv[3];                  // 当前程序的 AI 名字   
    int game_number = atoi(argv[4]);         // 最大对局数量
    vector<string> bots;
    for (int i = 5; i < argc; ++i)
    {
        string bot_name = argv[i];
        bots.push_back(bot_name);
    }
    int socket = connectServer();
    run(socket, room_id, room_number, name, game_number, bots);
    close(socket);
    return 0;
}