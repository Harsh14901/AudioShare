mkdir .cache
	
cd .\Server
npm ci 
npm run create-executable
Move-Item .\CAV_server.exe ..\.cache -force

cd ..\CLI

python3 -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
pip install -r dev-requirements.txt

cd .\cli

pyinstaller -F --add-data '..\..\.cache\CAV_server.exe;.' --add-data 'ffmpeg.exe;.' '.\main.py' -n LocalParty
Move-Item .\dist\LocalParty.exe ..\..\.cache\ -force

cd ..\..\Electron\ElectronGUI

mkdir binaries
Copy-Item ..\..\.cache\LocalParty.exe .\binaries\ -force
npm ci
npm run make
Move-Item out\ ..\..\dist\ -force
	
cd ..\..\

# rm -r .cache\ 
rm -r .\CLI\cli\build\;
rm -r .\CLI\cli\dist\;
rm .\CLI\cli\LocalParty.spec
rm -r .\Electron\ElectronGUI\binaries