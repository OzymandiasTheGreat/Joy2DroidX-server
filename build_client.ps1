Write-Host "`nBuilding ViGEmClient binaries..." -ForegroundColor Green
& .\vs2017.ps1
pushd ".\ViGEmClient\"
& .\build.ps1 -configuration Release_DLL
Copy-Item -Force -Path ".\bin\release\x64\ViGEmClient.dll" -Destination "..\j2dx\win\ViGEm\x64\ViGEmClient.dll"
Copy-Item -Force -Path ".\bin\release\x86\ViGEmClient.dll" -Destination "..\j2dx\win\ViGEm\x86\ViGEmClient.dll"
& git clean -dffx
& git reset --hard
popd
Write-Host "`nBinaries have been updated" -ForegroundColor Green
