#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <iostream>
using namespace std;

#define MYPORT  19999
#define MYIP "127.0.0.1" 
#define BUFFER_SIZE 10240
char sendbuf[BUFFER_SIZE];
char recvbuf[BUFFER_SIZE];
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
void sendData(int socket, string message)
{
    memset(sendbuf, 0, sizeof(sendbuf));
    strcpy(sendbuf, message.c_str());
    send(socket, sendbuf, strlen(sendbuf), 0);
}
void sendMessage(int socket, string message)
{
    int dataLength = strlen(message.c_str());
    sendLength(socket, dataLength);
    sendData(socket, message);
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
void recvData(int socket, int dataLength)
{
    memset(recvbuf, 0, sizeof(recvbuf));
    recv(socket, recvbuf, dataLength, 0);
    cout << recvbuf << endl;
}
void receiveMessage(int socket)
{
    int dataLength = recvLength(socket);
    recvData(socket, dataLength);
}
void run(int socket)
{
    sendMessage(socket, "Hello World cpp");
    receiveMessage(socket);
}
int main()
{
    int socket = connectServer();
    run(socket);
    close(socket);
    return 0;
}