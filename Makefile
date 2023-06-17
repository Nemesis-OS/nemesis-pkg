install:
	sudo cp main.py /usr/bin/nemesis-pkg
	sudo chmod +x /usr/bin/nemesis-pkg
	sudo mkdir /etc/nemesis-pkg
	sudo cp config.py /etc/nemesis-pkg/config.py
