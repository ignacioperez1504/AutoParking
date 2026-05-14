#ifndef PARQUEADERO_H
#define PARQUEADERO_H

#include <string>
#include <map>

// Numero total de celdas del parqueadero
const int TOTAL_CELDAS = 30;

// Estructura que representa una celda del parqueadero
struct Celda {
    bool ocupada;
    std::string placa;
    std::string horaIngreso;
};

class Parqueadero {
private:
    Celda celdas[TOTAL_CELDAS];              // Arreglo de 30 celdas (indices 0-29, pero representan celdas 1-30)
    std::map<std::string, int> placaACelda;            // Mapa: placa -> indice de celda

    // Obtiene la hora actual en formato HH:MM:SS
    std::string obtenerHoraActual();

public:
    // Constructor: inicializa todas las celdas como libres
    Parqueadero();

    // Registra o retira un vehiculo:
    // - Si la placa NO existe: asigna primera celda libre, devuelve celda y hora
    // - Si la placa YA existe: libera la celda, devuelve celda liberada
    // Retorna true si se registro (ingreso), false si se retiro (salida)
    bool registrarPlaca(std::string placa, std::string& celda, std::string& hora);

    // Devuelve un string con el estado completo de las 30 celdas
    std::string obtenerEstado();

    // Devuelve el estado simplificado: "1,0,1,..." para la DLL
    std::string obtenerEstadoRaw();
};

#endif // PARQUEADERO_H
