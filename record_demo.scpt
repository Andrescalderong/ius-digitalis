-- Abre el dashboard (asume servidor en 8000) y hace un scroll suave mientras graba
tell application "Google Chrome"
    activate
    if (count of windows) = 0 then make new window
    set theURL to "http://localhost:8000/dashboard_live.html"
    tell window 1
        if (count of tabs) = 0 then
            make new tab with properties {URL:theURL}
        else
            set URL of active tab to theURL
        end if
    end tell
end tell

delay 2

tell application "QuickTime Player"
    activate
end tell

tell application "System Events"
    -- Menú: Archivo → Nueva grabación de pantalla
    tell process "QuickTime Player"
        click menu item "Nueva grabación de pantalla" of menu "Archivo" of menu bar 1
        delay 1
        -- Clic en "Grabar" (puede requerir ajustar coordenadas según pantallas)
        click at {500, 300}
        delay 1
        key down space
        delay 0.3
        key up space
    end tell
end tell

-- Espera mientras haces scroll (simulado)
delay 2
tell application "System Events"
    repeat 30 times
        key code 125 -- Arrow Down
        delay 0.25
    end repeat
end tell

-- Detener grabación y guardar en Escritorio
tell application "QuickTime Player"
    tell document 1
        stop
        set savePath to (path to desktop as text) & "IUS-DIGITALIS-DEMO.mov"
        save in file savePath
        close saving no
    end tell
end tell
