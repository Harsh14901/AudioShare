cd Server
npm run create-executable
mv CAV_server ..\CLI\cli\

cd ..\CLI\cli\
make
cd ..\..\Electron\ElectronGUI

mkdir -p binaries
cp ..\..\CLI\cli\dist\LocalParty binaries\
npm run make
cd ..\..\
mkdir -p out
mv Electron\ElectronGUI\out\ .\

