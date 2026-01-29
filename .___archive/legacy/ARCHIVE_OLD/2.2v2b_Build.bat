@echo off
REM ==============================================================================
REM MSVC Build Script for 2.2v2b_ProcessManagerDocs.cpp
REM ==============================================================================
REM Pure C++ stdlib implementation - no external dependencies
REM ==============================================================================

echo Building 2.2v2b_ProcessManagerDocs.exe...

REM Initialize MSVC environment
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x64

REM Change to script directory
cd /d "%~dp0"

REM Compile with MSVC
REM /std:c++17 - C++17 standard
REM /O2 - Optimize for speed
REM /EHsc - Exception handling model
REM /W4 - Warning level 4
REM /Fe: - Output executable name
cl /std:c++17 /O2 /EHsc /W4 2.2v2b_ProcessManagerDocs.cpp /Fe:2.2v2b_ProcessManagerDocs.exe

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Compilation failed!
    exit /b 1
)

echo Build successful: 2.2v2b_ProcessManagerDocs.exe
exit /b 0
