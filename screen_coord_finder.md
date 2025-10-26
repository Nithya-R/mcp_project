# Mouse Position Tracker

## Purpose
This PowerShell script continuously tracks and displays the current **mouse cursor position** on your screen.  
It updates every second and shows the X and Y coordinates in real-time. Useful for:
- Debugging
- UI automation
- Creating tools that rely on screen coordinates

---

## Script (All-in-One)

```powershell
# Add the MousePosition class definition
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public class MousePosition {
    [StructLayout(LayoutKind.Sequential)]
    public struct POINT {
        public int X;
        public int Y;
    }

    [DllImport("user32.dll")]
    public static extern bool GetCursorPos(out POINT lpPoint);
}
"@

# Main loop to display cursor position
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
