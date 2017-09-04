all: nothing

nothing:
	@echo "Run 'sudo make install' to install notes to your system."

install:
	cp notes.py /usr/local/bin/notes
	chmod +x /usr/local/bin/notes
	ln -fs /usr/local/bin/notes /usr/local/bin/note
