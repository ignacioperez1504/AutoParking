#ifndef LIBRERIA_H
#define LIBRERIA_H

#ifdef _WIN32
#define EXPORT extern "C" __declspec(dllexport)
#else
#define EXPORT extern "C"
#endif

// Inicializa el sistema de parqueadero
EXPORT void inicializar();

// Procesa una placa: Entrada o Salida. Llena resultado con "CELDA|HORA|ESTADO"
EXPORT void procesarPlaca(const char* placa, char* resultado);

// Obtiene el estado de las 30 celdas separado por comas: "1,0,1,..." (1=ocupada, 0=libre)
EXPORT void obtenerEstadoCeldas(char* buffer);

#endif // LIBRERIA_H
