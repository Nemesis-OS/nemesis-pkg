install:
	@echo "installing npkg-cfgen"
	install -Dm755 genconfig.py /usr/bin/npkg-cfgen
	@echo "installing nemesis-pkg"
	install -Dm755 main.py /usr/bin/npkg
	install -Dm755 main.py /usr/bin/nemesis-pkg
	mkdir -p /etc/nemesis-pkg
	@echo "note: please run npkg-cfgen to generate nemesis-pkg config"
build:
	@echo "Building main.py"
	pyinstaller --noconfirm --onefile --console "main.py"
	@echo "Building genconfig.py"
	pyinstaller --noconfirm --onefile --console "genconfig.py"
	@echo "Installing npkg-cfgen"
	install -Dm755 dist/genconfig /usr/bin/npkg-cfgen
	@echo "Installing nemesis-pkg"
	install -Dm755 dist/main /usr/bin/npkg
	install -Dm755 dist/main /usr/bin/nemesis-pkg
	mkdir -p /etc/nemesis-pkg
	@echo "Note: Please run npkg-cfgen to generate nemesis-pkg config"
