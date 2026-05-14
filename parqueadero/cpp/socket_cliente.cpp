#include "socket_cliente.h"
#include <iostream>

#pragma comment(lib, "ws2_32.lib")

SocketCliente::SocketCliente() : sock(INVALID_SOCKET), conectado(false) {
  // Inicializar Winsock
  if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
    std::cerr << "Error: No se pudo inicializar Winsock." << std::endl;
  }
}

SocketCliente::~SocketCliente() {
  desconectar();
  WSACleanup();
}

bool SocketCliente::conectar(std::string ip, int puerto) {
  if (conectado)
    return true;

  sock = socket(AF_INET, SOCK_STREAM, 0);
  if (sock == INVALID_SOCKET) {
    std::cerr << "Error: No se pudo crear el socket." << std::endl;
    return false;
  }

  sockaddr_in serverAddr;
  serverAddr.sin_family = AF_INET;
  serverAddr.sin_port = htons(puerto);
  serverAddr.sin_addr.s_addr = inet_addr(ip.c_str());

  if (connect(sock, (struct sockaddr *)&serverAddr, sizeof(serverAddr)) ==
      SOCKET_ERROR) {
    std::cerr << "Error: No se pudo conectar al servidor " << ip << ":"
              << puerto << std::endl;
    closesocket(sock);
    return false;
  }

  conectado = true;
  std::cout << "[SOCKET] Conectado exitosamente al servidor." << std::endl;
  return true;
}

bool SocketCliente::enviarMensaje(std::string mensaje) {
  if (!conectado) {
    std::cerr << "Error: No hay conexion activa para enviar el mensaje."
              << std::endl;
    return false;
  }

  int bytesEnviados = send(sock, mensaje.c_str(), mensaje.length(), 0);
  if (bytesEnviados == SOCKET_ERROR) {
    std::cerr << "Error: No se pudo enviar el mensaje." << std::endl;
    desconectar();
    return false;
  }

  return true;
}

void SocketCliente::desconectar() {
  if (conectado) {
    closesocket(sock);
    sock = INVALID_SOCKET;
    conectado = false;
    std::cout << "[SOCKET] Desconectado." << std::endl;
  }
}
