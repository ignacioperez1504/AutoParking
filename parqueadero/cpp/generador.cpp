#include "generador.h"
#include <cstdlib>
#include <ctime>

using namespace std;

// Genera una placa colombiana aleatoria con formato: ABC-123
string generarPlaca() {
    string placa = "";

    // 3 letras mayusculas (A-Z)
    for (int i = 0; i < 3; i++) {
        char letra = 'A' + (rand() % 26);
        placa += letra;
    }

    placa += "-";

    // 3 digitos (0-9)
    for (int i = 0; i < 3; i++) {
        char digito = '0' + (rand() % 10);
        placa += digito;
    }

    return placa;
}
