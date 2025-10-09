$log = Get-Item .\patch_font.log
Push-Location ..\edsl
git log -1 --oneline | Tee-Object $log
Pop-Location
Copy-Item ..\edsl\lak\bld\LAK.ttf .
&'C:\Program Files (x86)\FontForgeBuilds\bin\ffpython.exe' .\patch_font.py | Tee-Object -Append $log
Invoke-WebRequest https://github.com/eggrobin/Nabu-ninua-ihsus/raw/refs/heads/master/Nabuninuaihsus.ttf -OutFile Nabuninuaihsus.ttf
$(Get-Content $log) | Out-File -Encoding utf8 $log