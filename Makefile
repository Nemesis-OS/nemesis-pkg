install:

do lscpu
go to where it says flags under BogoMIPS and above virtualization features
copy all those flags now add it to yours text editor(just anything to hold it)
now do ```python``` do the following

flags_str = (add your flags you copied into the text editor from above)
cpu_flags = sorted(flags_str.split())
cpu_flags

now copy this and go back to your text editor now place it

sudo vim /home/addusrhere/nemesis-pkg

go to where it says 
cpu_flags = [] # insert cpu flags here..
add the cpu flags you pasted into your text editor 
exit vim:)
now do the following commands


	sudo cp main.py /usr/bin/nemesis-pkg
	sudo chmod +x /usr/bin/nemesis-pkg
	sudo mkdir /etc/nemesis-pkg
	sudo cp config.py /etc/nemesis-pkg/config.py
