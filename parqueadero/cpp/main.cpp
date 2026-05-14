#include <iostream>
#include <string>
#include <thread>
#include <chrono>
#include <cstdlib>
#include <ctime>
#include "generador.h"
#include "parqueadero.h"
#include "socket_cliente.h"

using namespace std;

int main() {
    srand(time(0));
    
    string ipServidor;
    cout << "============================================" << endl;
    cout << "      AUTOPARKING - CLIENTE C++" << endl;
    cout << "============================================" << endl;
    cout << "Ingrese la IP del servidor: ";
    cin >> ipServidor;

    // Inicializar objetos
    Parqueadero parking;
    SocketCliente cliente;

    // Intentar conectar al servidor en el puerto 5000
    if (!cliente.conectar(ipServidor, 5000)) {
        cout << "[ERROR] No se pudo establecer conexion inicial. Asegurese de que el servidor este corriendo." << endl;
        // Aun asi continuamos para que el usuario vea el proceso, aunque no se envien mensajes
    }

    cout << "\nIniciando simulacion automatica..." << endl;
    cout << "Presione Ctrl+C para detener." << endl;
    cout << "--------------------------------------------" << endl;

    while (true) {
        // 1. Generar placa aleatoria
        string placa = generarPlaca();
        
        // 2. Procesar en el parqueadero
        string celda, hora;
        bool esIngreso = parking.registrarPlaca(placa, celda, hora);
        string estadoStr = esIngreso ? "ENTRADA" : "SALIDA";

        // Caso especial: Parqueadero lleno
        if (esIngreso && celda == "-1") {
            cout << "[LLENO] Intento de ingreso: " << placa << " - No hay celdas libres." << endl;
        } else {
            // 3. Mostrar en consola
            cout << "[" << estadoStr << "] Placa: " << placa 
                 << " | Celda: " << celda 
                 << " | Hora: " << hora << endl;

            // 4. Enviar por Socket: "PLACA|HORA|CELDA|ESTADO"
            string mensaje = placa + "|" + hora + "|" + celda + "|" + estadoStr;
            cliente.enviarMensaje(mensaje);
        }

        // 5. Esperar tiempo aleatorio entre 2 y 5 segundos
        int espera = 2 + (rand() % 4); // 2, 3, 4 o 5
        this_thread::sleep_for(chrono::seconds(espera));
    }

    return 0;
}
