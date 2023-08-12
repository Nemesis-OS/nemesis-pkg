install:
	@echo "installing npkg-cfgen"
	install -Dm755 genconfig.py /usr/bin/npkg-cfgen
	@echo "installing nemesis-pkg"
	install -Dm755 main.py /usr/bin/npkg
	install -Dm755 main.py /usr/bin/nemesis-pkg
	mkdir /etc/nemesis-pkg
	@echo "note: please run npkg-cfgen to generate nemesis-pkg config"
