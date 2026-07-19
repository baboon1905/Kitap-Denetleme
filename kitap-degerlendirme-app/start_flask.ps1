$pinfo = New-Object System.Diagnostics.ProcessStartInfo
$pinfo.FileName = "C:\Users\fatih\MASAST~1\KITAPD~1\kitap-degerlendirme-app\venv\Scripts\pythonw.exe"
$pinfo.Arguments = "C:\Users\fatih\MASAST~1\KITAPD~1\kitap-degerlendirme-app\run_flask.py"
$pinfo.WorkingDirectory = "C:\Users\fatih\MASAST~1\KITAPD~1\kitap-degerlendirme-app"
$pinfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
[System.Diagnostics.Process]::Start($pinfo)

