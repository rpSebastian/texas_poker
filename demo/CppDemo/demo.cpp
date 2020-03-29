#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <iostream>
#include "CJsonObject.hpp"
#include "cJSON.h"
#include <vector>
#include <string>
using namespace std;

#define MYPORT  18888
#define MYIP "127.0.0.1"
#define BUFFER_SIZE 1024
char sendbuf[BUFFER_SIZE];
char recvbuf[BUFFER_SIZE];
typedef neb::CJsonObject json;

int connectServer()
{
    int sock_cli = socket(AF_INET,SOCK_STREAM, 0);
    struct sockaddr_in servaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(MYPORT); 
    servaddr.sin_addr.s_addr = inet_addr(MYIP);  
    if (connect(sock_cli, (struct sockaddr *)&servaddr, sizeof(servaddr)) < 0)
    {
        perror("connect error");
        exit(1);
    }
    return sock_cli;
}
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
string connectMessage(int room_id, string name, int room_number, vector<string> bots)
{
    json message;
    message.Add("room_id", "room_id");
    message.Add("name", name);
    message.Add("room_number", room_number);
    message.AddEmptySubArray("bots");
    for (int i = 0; i < (int)bots.size(); ++i)
    {
        message["bots"].Add(bots[i]);
    }
    cout << message.ToString() << endl;
    return message.ToString();
}
string startMessage()
{
    json message;
    message.Add("info", "start");
    return message.ToString();
}
void run(int socket)
{
    json message;
    sendMessage(socket, connectMessage(1, "Alice", 2, vector<string> {"CallAgent"}));
    message = receiveMessage(socket);
    cout << message.ToFormattedString() << endl;
    sendMessage(socket, startMessage());
    while (true)
    {
        message = receiveMessage(socket);
        cout << message.ToFormattedString() << endl;
        if (message("info") == "state" && message("position") == message("action_position"))
        {
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
        if (message("info") == "result")
        {   
            break;
            sendMessage(socket, startMessage());
        }
    }
}
int main()
{
    int socket = connectServer();
    run(socket);
    close(socket);
    return 0;
}