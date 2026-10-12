# ==============================================================================
# Script de PowerShell: Registrar Tareas Programadas para BME Contest Live Engine
# 1. Tarea de Tarde (Recomendación y Compra): Lunes a Jueves a las 17:15 CET
# 2. Tarea de Mañana (Salida y Venta T+1): Martes a Viernes a las 09:00 CET
# ==============================================================================

$WorkingDirectory = "d:\Escritorio\Profesional\BME contest"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " CONFIGURACION DEL PROGRAMADOR DE TAREAS DE WINDOWS (BME CONTEST)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "Ruta de Trabajo: $WorkingDirectory"

# Configuración compartida de batería/energía
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# ------------------------------------------------------------------------------
# 1. TAREA DE LA TARDE (17:15 CET): Recomendación y Registro de Compra
# ------------------------------------------------------------------------------
$TaskBuyName = "BME_Contest_EveningBuy"
$CmdBuy = "Set-Location 'd:\Escritorio\Profesional\BME contest'; python scripts/run_live_recommendation.py"
$ActionBuy = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoExit -Command `"$CmdBuy`"" -WorkingDirectory $WorkingDirectory
$TriggerBuy = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday, Tuesday, Wednesday, Thursday -At 17:15

try {
    # Eliminar antigua si existe
    $oldBuy = Get-ScheduledTask -TaskName $TaskBuyName -ErrorAction SilentlyContinue
    if ($oldBuy) { Unregister-ScheduledTask -TaskName $TaskBuyName -Confirm:$false }
    
    # También limpiar el nombre anterior si existía
    $legacy = Get-ScheduledTask -TaskName "BME_Contest_LiveRecommender" -ErrorAction SilentlyContinue
    if ($legacy) { Unregister-ScheduledTask -TaskName "BME_Contest_LiveRecommender" -Confirm:$false }

    Register-ScheduledTask -TaskName $TaskBuyName -Action $ActionBuy -Trigger $TriggerBuy -Settings $Settings -Description "BME Contest: Recomendación y registro de compra diaria (17:15 CET)"
    Write-Host "`n[EXITO] Tarea 1 Registrada: '$TaskBuyName'" -ForegroundColor Green
    Write-Host "  -> Horario: Lunes a Jueves a las 17:15 CET"
} catch {
    Write-Host "`n[ERROR] No se pudo registrar '$TaskBuyName': $($_.Exception.Message)" -ForegroundColor Red
}

# ------------------------------------------------------------------------------
# 2. TAREA DE LA MAÑANA (09:00 CET): Salida y Registro de Venta T+1
# ------------------------------------------------------------------------------
$TaskSellName = "BME_Contest_MorningSell"
$CmdSell = "Set-Location 'd:\Escritorio\Profesional\BME contest'; python scripts/run_morning_exit.py"
$ActionSell = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoExit -Command `"$CmdSell`"" -WorkingDirectory $WorkingDirectory
$TriggerSell = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Tuesday, Wednesday, Thursday, Friday -At 09:00

try {
    $oldSell = Get-ScheduledTask -TaskName $TaskSellName -ErrorAction SilentlyContinue
    if ($oldSell) { Unregister-ScheduledTask -TaskName $TaskSellName -Confirm:$false }

    Register-ScheduledTask -TaskName $TaskSellName -Action $ActionSell -Trigger $TriggerSell -Settings $Settings -Description "BME Contest: Salida de apertura y registro de venta T+1 (09:00 CET)"
    Write-Host "`n[EXITO] Tarea 2 Registrada: '$TaskSellName'" -ForegroundColor Green
    Write-Host "  -> Horario: Martes a Viernes a las 09:00 CET"
} catch {
    Write-Host "`n[ERROR] No se pudo registrar '$TaskSellName': $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=================================================================" -ForegroundColor Cyan
Write-Host " RESUMEN DE AUTOMATIZACION" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "1. A las 17:15 CET (L-J): Se abre la ventana para ver CS vs NR10 y registrar la compra."
Write-Host "2. A las 09:00 CET (M-V): Se abre la ventana para ejecutar y registrar la venta de salida."
Write-Host "`nPara probar las tareas manualmente ahora mismo:"
Write-Host "  Start-ScheduledTask -TaskName '$TaskBuyName'" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName '$TaskSellName'" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan
