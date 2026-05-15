#define _CRT_SECURE_NO_WARNINGS
#include "parqueadero.h"
#include <ctime>
#include <sstream>
#include <iomanip>
#include <vector>
#include <cstdlib>

using namespace std;

// Constructor: inicializa todas las celdas como LIBRES
Parqueadero::Parqueadero() {
    for (int i = 0; i < TOTAL_CELDAS; i++) {
        celdas[i].ocupada = false;
        celdas[i].placa = "";
        celdas[i].horaIngreso = "";
    }
}

// Obtiene la hora actual del sistema en formato HH:MM:SS
string Parqueadero::obtenerHoraActual() {
    time_t ahora = time(0);
    struct tm* tiempoLocal = localtime(&ahora);

    ostringstream oss;
    oss << setfill('0') << setw(2) << tiempoLocal->tm_hour << ":"
        << setfill('0') << setw(2) << tiempoLocal->tm_min  << ":"
        << setfill('0') << setw(2) << tiempoLocal->tm_sec;

    return oss.str();
}

// Registra ingreso o salida de un vehiculo
// Retorna true si fue INGRESO, false si fue SALIDA
bool Parqueadero::registrarPlaca(string placa, string& celda, string& hora) {

    // Caso 1: La placa YA existe -> SALIDA (liberar celda)
    if (placaACelda.find(placa) != placaACelda.end()) {
        int indice = placaACelda[placa];

        // Guardar info antes de liberar
        celda = to_string(indice + 1);  // Celda 1-30
        hora = celdas[indice].horaIngreso;

        // Liberar la celda
        celdas[indice].ocupada = false;
        celdas[indice].placa = "";
        celdas[indice].horaIngreso = "";

        // Eliminar del mapa
        placaACelda.erase(placa);

        return false;  // Fue una SALIDA
    }

    // Caso 2: La placa NO existe -> INGRESO (ELEGIR CELDA AL AZAR)
    vector<int> celdasLibres;
    for (int i = 0; i < TOTAL_CELDAS; i++) {
        if (!celdas[i].ocupada) {
            celdasLibres.push_back(i);
        }
    }

    // Si hay celdas libres disponibles
    if (!celdasLibres.empty()) {
        // Elegir un indice al azar del vector de celdas libres
        int r = rand() % celdasLibres.size();
        int indiceElegido = celdasLibres[r];

        string horaActual = obtenerHoraActual();

        // Ocupar la celda
        celdas[indiceElegido].ocupada = true;
        celdas[indiceElegido].placa = placa;
        celdas[indiceElegido].horaIngreso = horaActual;

        // Registrar en el mapa
        placaACelda[placa] = indiceElegido;

        // Devolver info
        celda = to_string(indiceElegido + 1);  // Celda 1-30
        hora = horaActual;

        return true;  // Fue un INGRESO
    }

    // Parqueadero lleno
    celda = "-1";
    hora = "";
    return true;
}

// Devuelve un string con el estado de las 30 celdas
string Parqueadero::obtenerEstado() {
    ostringstream oss;

    oss << "\n========================================" << endl;
    oss << "   ESTADO DEL PARQUEADERO (30 celdas)" << endl;
    oss << "========================================" << endl;

    for (int i = 0; i < TOTAL_CELDAS; i++) {
        oss << "  Celda " << setw(2) << setfill('0') << (i + 1) << ": ";

        if (celdas[i].ocupada) {
            oss << "[OCUPADA] Placa: " << celdas[i].placa
                << " | Hora ingreso: " << celdas[i].horaIngreso;
        } else {
            oss << "[LIBRE]";
        }

        oss << endl;
    }

    oss << "========================================" << endl;

    return oss.str();
}

// Devuelve el estado simplificado: "1,0,1,..." (1=ocupada, 0=libre)
string Parqueadero::obtenerEstadoRaw() {
    string raw = "";
    for (int i = 0; i < TOTAL_CELDAS; i++) {
        raw += (celdas[i].ocupada ? "1" : "0");
        if (i < TOTAL_CELDAS - 1) raw += ",";
    }
    return raw;
}
