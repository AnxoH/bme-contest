# ==============================================================================
# Script de PowerShell: Registrar Tarea Programada para BME Contest Live Engine
# Horario: Lunes a Jueves a las 17:15 CET
# ==============================================================================

$TaskName = "BME_Contest_LiveRecommender"
$WorkingDirectory = "d:\Escritorio\Profesional\BME contest"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " CONFIGURACION DEL PROGRAMADOR DE TAREAS DE WINDOWS (BME CONTEST)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "Ruta de Trabajo: $WorkingDirectory"
Write-Host "Hora de Ejecucion: 17:15 CET (Lunes a Jueves)"

# Accion: Abrir una ventana interactiva de PowerShell con el script ejecutado
$ScriptCommand = "Set-Location 'd:\Escritorio\Profesional\BME contest'; python scripts/run_live_recommendation.py"
$Argument = "-NoExit -Command `"$ScriptCommand`""
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $Argument -WorkingDirectory $WorkingDirectory

# Disparador: Semanal Lunes, Martes, Miercoles y Jueves a las 17:15
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday, Tuesday, Wednesday, Thursday -At 17:15

# Configuracion adicional
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Registrar o actualizar tarea
try {
    $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existing) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Tarea previa eliminada para actualizar configuracion..." -ForegroundColor Yellow
    }
    
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Ejecucion diaria del motor de recomendaciones BME Contest a las 17:15 CET"
    
    Write-Host "`n[EXITO] Tarea '$TaskName' registrada correctamente en Windows." -ForegroundColor Green
    Write-Host "Se ejecutara de Lunes a Jueves a las 17:15 CET abriendo una ventana con las recomendaciones."
    Write-Host "`nPara probar la tarea ahora mismo manualmente, ejecuta:"
    Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Yellow
} catch {
    Write-Host "`n[ERROR] No se pudo registrar la tarea." -ForegroundColor Red
    Write-Host $_.Exception.Message
}
