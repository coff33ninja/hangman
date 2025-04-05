@echo off
echo Clearing training data while preserving core files...

:: Define the data folder
set DATA_FOLDER=data

:: Change to the data folder
cd %DATA_FOLDER%

:: Delete all files except the core files
for %%f in (*) do (
    if /i not "%%f"=="symbols.json" if /i not "%%f"=="predefined_words.json" if /i not "%%f"=="core_language_components.json" if /i not "%%f"=="words.txt" if /i not "%%f"=="riddles_easy.txt" if /i not "%%f"=="riddles_medium.txt" if /i not "%%f"=="riddles_hard.txt" if /i not "%%f"=="scores.json" if /i not "%%f"=="achievements.json" if /i not "%%f"=="riddles.txt" (
        del "%%f"
    )
)

:: Delete all files in the topics folder
if exist topics (
    cd topics
    del *.*
    cd ..
)

:: Return to the original directory
cd ..

echo Training data cleared successfully!
pause