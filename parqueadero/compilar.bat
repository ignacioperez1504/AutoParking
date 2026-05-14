@echo off
echo ===================================================
echo   AUTOPARKING - Compilador de C++ (Windows g++)
echo ===================================================
echo.

cd cpp

:: 1. Compilar el ejecutable principal
echo [1/3] Compilando autoparking.exe...
g++ main.cpp generador.cpp parqueadero.cpp socket_cliente.cpp -o autoparking.exe -lws2_32
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Error al compilar autoparking.exe
    pause
    exit /b %errorlevel%
)
echo [OK] autoparking.exe compilado con exito.
echo.

:: 2. Compilar la libreria DLL
echo [2/3] Compilando libreria.dll...
g++ -shared -o libreria.dll libreria.cpp parqueadero.cpp -lws2_32
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Error al compilar libreria.dll
    pause
    exit /b %errorlevel%
)
echo [OK] libreria.dll compilada con exito.
echo.

:: 3. Copiar la DLL a la carpeta de Python
echo [3/3] Copiando libreria.dll a ../python/...
copy /y libreria.dll "..\python\libreria.dll" >nul
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] No se pudo copiar la DLL a la carpeta python.
    pause
    exit /b %errorlevel%
)
echo [OK] DLL copiada correctamente.
echo.

cd ..

echo ===================================================
echo   PROCESO COMPLETADO EXITOSAMENTE
echo ===================================================
echo Puedes cerrar esta ventana.
echo.
pause
