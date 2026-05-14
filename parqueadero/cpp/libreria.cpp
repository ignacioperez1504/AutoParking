#include "libreria.h"
#include "parqueadero.h"
#include <cstring>
#include <string>
#include <sstream>

// Instancia global del parqueadero para la DLL
static Parqueadero* g_parqueadero = nullptr;

void inicializar() {
    if (g_parqueadero != nullptr) {
        delete g_parqueadero;
    }
    g_parqueadero = new Parqueadero();
}

void procesarPlaca(const char* placa, char* resultado) {
    if (g_parqueadero == nullptr) {
        strcpy(resultado, "ERROR|0|0");
        return;
    }

    std::string s_placa(placa);
    std::string s_celda, s_hora;
    
    // registrarPlaca devuelve true si es INGRESO, false si es SALIDA
    bool esIngreso = g_parqueadero->registrarPlaca(s_placa, s_celda, s_hora);
    
    std::string estado = esIngreso ? "ENTRADA" : "SALIDA";
    
    // Si es ingreso y devuelve celda -1 es que esta lleno
    if (esIngreso && s_celda == "-1") {
        strcpy(resultado, "LLENO|0|ERROR");
        return;
    }

    std::string res = s_celda + "|" + s_hora + "|" + estado;
    strcpy(resultado, res.c_str());
}

void obtenerEstadoCeldas(char* buffer) {
    if (g_parqueadero == nullptr) {
        strcpy(buffer, "");
        return;
    }

    std::string raw = g_parqueadero->obtenerEstadoRaw();
    strcpy(buffer, raw.c_str());
}
