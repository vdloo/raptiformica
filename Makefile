.PHONY: all clean

NAME := raptiformica
VERSION := 0.1
MAINTAINER := Rick van de Loo <rickvandeloo@gmail.com>
DESCRIPTION := Decentralized server orchestration

test:
	./runtests.sh -1
install:
	sudo mkdir -p /usr/share/raptiformica
	sudo cp -R . /usr/share/raptiformica
	sudo ln -sf /usr/share/raptiformica/bin/raptiformica /usr/bin/raptiformica
	sudo chmod u+x /usr/bin/raptiformica
uninstall:
	sudo rm -rf /usr/share/raptiformica
	sudo rm -f /usr/bin/raptiformica
clean:
	git clean -xfd

