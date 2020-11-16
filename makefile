.ONESHELL:
all:
	cd Server
	npm run create-executable
	yes | mv CAV_server ../CLI/cli/
	
	cd ../CLI/cli/
	make
	cd ../../Electron/ElectronGUI
	
	mkdir -p binaries
	yes | cp ../../CLI/cli/dist/LocalParty binaries/
	npm run make

	cd ../../
	ln -s Electron/ElectronGUI/out/ out

