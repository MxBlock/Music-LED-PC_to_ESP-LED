#include <iostream>
#include <string>
#include <winsock2.h>
#include <cstdint>
#include <stdlib.h>

int main()
{   
    // Thanks to Mikolasan and KMcN
    // See https://stackoverflow.com/questions/24559909/sending-string-over-udp-in-c

    // Initialise Winsock DLL
    // See https://beej.us/guide/bgnet/html/#windows 
    WSADATA wsaData;      
    // MAKEWORD(1,1) for Winsock 1.1, MAKEWORD(2,0) for Winsock 2.0
    if (WSAStartup(MAKEWORD(1, 1), &wsaData) != 0) {
        fprintf(stderr, "WSAStartup failed.\n");
        exit(1);
    }
    
    // Set up connection and send
    std::string hostname{"192.168.168.193"};
    uint16_t port = 80;
    SOCKET sock = ::socket(AF_INET, SOCK_DGRAM, 0);
     
    sockaddr_in destination;
    destination.sin_family = AF_INET;
    destination.sin_port = htons(port);
    destination.sin_addr.s_addr = inet_addr(hostname.c_str());

    uint8_t rgb[3] = {255, 0, 155};
    uint8_t one[3] = {1, 1, 1};

    while(true){
        std::string msg = std::to_string(rgb[0]) + "," + std::to_string(rgb[1]) + "," + std::to_string(rgb[2]);
        int n_bytes = ::sendto(sock, msg.c_str(), msg.length(), 0, reinterpret_cast<sockaddr*>(&destination), sizeof(destination));
        std::cout << n_bytes << " bytes sent" << std::endl;
        //std::cin.ignore(); //wait for user press enter

        for (int i=0; i < 3; ++i) {
            rgb[i] += one[i];
        }

        Sleep(10);
    }
    ::closesocket(sock);
    // Clean up sockets library
    WSACleanup();
    return 0;
}