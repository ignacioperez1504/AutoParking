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
    // Inicializar semilla para numeros aleatorios
    srand(time(0));
    
    string ipServidor;
    cout << "============================================" << endl;
    cout << "      AUTOPARKING - CLIENTE C++" << endl;
    cout << "============================================" << endl;
    cout << "Ingrese la IP del servidor (Computador 2): ";
    cin >> ipServidor;

    // Inicializar objetos
    Parqueadero parking;
    SocketCliente cliente;

    // Intentar conectar al servidor en el puerto 5000
    if (!cliente.conectar(ipServidor, 5000)) {
        cout << "[ERROR] No se pudo establecer conexion inicial con el servidor." << endl;
        cout << "Asegurese de que el servidor Python este corriendo y la IP sea correcta." << endl;
    }

    cout << "\nIniciando simulacion automatica (Asignacion Aleatoria)..." << endl;
    cout << "Presione Ctrl+C para detener." << endl;
    cout << "--------------------------------------------" << endl;

    while (true) {
        // 1. Generar placa aleatoria
        string placa = generarPlaca();
        
        // 2. Procesar en el parqueadero (Ahora elige celda al azar)
        string celda, hora;
        bool esIngreso = parking.registrarPlaca(placa, celda, hora);
        string estadoStr = esIngreso ? "ENTRADA" : "SALIDA";

        // Caso especial: Parqueadero lleno
        if (esIngreso && celda == "-1") {
            cout << "[LLENO] Intento de ingreso: " << placa << " - Sin espacio disponible." << endl;
        } else {
            // 3. Mostrar en consola
            cout << "[" << estadoStr << "] Placa: " << placa 
                 << " | Celda Asignada: " << celda 
                 << " | Hora: " << hora << endl;

            // 4. Enviar por Socket: "PLACA|HORA|CELDA|ESTADO"
            string mensaje = placa + "|" + hora + "|" + celda + "|" + estadoStr;
            cliente.enviarMensaje(mensaje);
        }

        // 5. Tiempo aleatorio real entre 2 y 5 segundos
        int espera = 2 + (rand() % 4); // Genera 2, 3, 4 o 5
        
        // Usamos std::this_thread::sleep_for para una espera precisa
        this_thread::sleep_for(chrono::seconds(espera));
    }

    return 0;
}
