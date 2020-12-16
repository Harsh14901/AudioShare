mkdir -p .cache

python.exe -m venv venv
.\venv\Scripts\Activate.ps1
cd CLI
pip install -r requirements.txt
pip install -r dev-requirements.txt
	
cd ..\Server
npm ci 
npm run create-executable
Move-Item .\CAV_server.exe ..\.cache -force
	
cd ..\CLI\cli
pyinstaller -F --add-data '..\..\.cache\CAV_server.exe;.' .\main.py -n LocalParty
Move-Item .\dist\LocalParty.exe ..\..\.cache\ -force

cd ..\..
mkdir -p .\Electron\ElectronGUI\binaries\
Copy-Item .cache\LocalParty.exe .\Electron\ElectronGUI\binaries\ -force
cd Electron\ElectronGUI\
npm ci
npm run make
mv out\ ..\..\dist\
	
rm -rf .cache\ 
cd CLI\cli
rm -rf build\ LocalParty.spec;