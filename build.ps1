# Définition du chemin vers le script Python
$scriptPath = "main.py"

# Construction de l'exécutable avec PyInstaller
& pyinstaller.exe --onefile $scriptPath --name "epub-sorter"

# Vérification de l'existence du dossier dist après la construction
if (Test-Path -Path ".\dist") {
    Write-Host "L'exécutable a été créé avec succès."
} else {
    Write-Host "Erreur lors de la création de l'exécutable."
}
