install:
	sudo cp main.py /usr/bin/nemesis-pkg
	chmod +x /usr/bin/nemesis-pkg
	mkdir /etc/nemesis-pkg
	sudo cp config.py /etc/nemesis-pkg/config.py
