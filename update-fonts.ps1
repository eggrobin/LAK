Push-Location ..\edsl
git log -1
Pop-Location
Copy-Item ..\edsl\lak\bld\LAK.ttf .
&'C:\Program Files (x86)\FontForgeBuilds\bin\ffpython.exe' .\patch_font.py
Invoke-WebRequest https://github.com/eggrobin/Nabu-ninua-ihsus/raw/refs/heads/master/Nabuninuaihsus.ttf -OutFile Nabuninuaihsus.ttf