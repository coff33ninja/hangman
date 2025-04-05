:: filepath: c:\Users\DRAGOHN\Documents\GitHub\hangman\clear_training_data.bat
@echo off
echo Clearing training data while preserving essential files...

:: Define the data folder
set DATA_FOLDER=data

:: Change to the data folder
cd %DATA_FOLDER%

:: Delete all files except the essential ones
for %%f in (*) do (
    if /i not "%%f"=="symbols.json" if /i not "%%f"=="predefined_words.json" if /i not "%%f"=="core_language_components.json" (
        del "%%f"
    )
)

:: Return to the original directory
cd ..

echo Training data cleared successfully!
pause