while ($true) {
    # Create a POINT struct and get current cursor position
    [MousePosition+POINT]$p = New-Object MousePosition+POINT
    [MousePosition]::GetCursorPos([ref]$p) | Out-Null

    # Clear previous output
    Clear-Host

    # Print the coordinates
    Write-Host "🖱️  Current Mouse Position"
    Write-Host "--------------------------"
    Write-Host ("X: {0}" -f $p.X)
    Write-Host ("Y: {0}" -f $p.Y)

    # Wait 1 second before updating
    Start-Sleep -Seconds 1
}