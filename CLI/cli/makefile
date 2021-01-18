clean:first
	rm -rf build/ LocalParty.spec

first:CAV_server
	pyinstaller -F --add-data './CAV_server:.'  ./main.py -n LocalParty
	mkdir -p ../ElectronGUI/binaries
	cp dist/LocalParty ../ElectronGUI/binaries/


