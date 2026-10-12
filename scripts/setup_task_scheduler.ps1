# ==============================================================================
# Script de PowerShell: Registrar Tarea Programada para BME Contest Live Engine
# Horario: Lunes a Jueves a las 17:15 CET
# ==============================================================================

$TaskName = "BME_Contest_LiveRecommender"
$WorkingDirectory = "d:\Escritorio\Profesional\BME contest"
$PythonPath = (Get-Command python).Source

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " CONFIGURACIÓN DEL PROGRAMADOR DE TAREAS DE WINDOWS (BME CONTEST)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "Ruta de Trabajo: $WorkingDirectory"
Write-Host "Intérprete Python: $PythonPath"
Write-Host "Hora de Ejecución: 17:15 CET (Lunes a Jueves)"

# Acción: Abrir una ventana de PowerShell interactiva que mantenga la salida abierta (-NoExit)
$Argument = "-NoExit -Command `"Set-Location '$WorkingDirectory'; python scripts/run_live_recommendation.py`""
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $Argument -WorkingDirectory $WorkingDirectory

# Disparador: Semanal Lunes, Martes, Miércoles y Jueves a las 17:15
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday, Tuesday, Wednesday, Thursday -At 17:15

# Configuración adicional
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Registrar o actualizar tarea
try {
    # Comprobar si ya existe para sobrescribir
    $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existing) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Tarea previa eliminada para actualizar configuración..." -ForegroundColor Yellow
    }
    
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Ejecución diaria del motor de recomendaciones BME Contest a las 17:15 CET"
    
    Write-Host "`n[ÉXITO] Tarea '$TaskName' registrada correctamente en Windows." -ForegroundColor Green
    Write-Host "Se ejecutará de Lunes a Jueves a las 17:15 abriendo una ventana con las recomendaciones."
    Write-Host "`nPara probar la tarea ahora mismo manualmente, puedes ejecutar:"
    Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Yellow
} catch {
    Write-Host "`n[ERROR] No se pudo registrar la tarea. Asegúrate de ejecutar PowerShell con permisos adecuados." -ForegroundColor Red
    Write-Host $_.Exception.Message
}
