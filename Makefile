# -*- Makefile for file_server files -*-
# Copyright 2013 Saevon <saevon.kyomae@gmail.com>
# TODO: install completions file?

.PHONY: default
default: all


COMPLETION_FILE=../completion.makefile
ifneq ($(wildcard ${COMPLETION_FILE}),${COMPLETION_FILE})
.PHONY: completion
completion:
	@ln -i -s ${PWD}/*.complete.bash ${HOME}/.bash_completion.d/ || true
else
include ../variables.makefile
include ${COMPLETION_FILE}
endif

.PHONY: all
all: main completion done



.PHONY: main
main:
	@echo "Setting up file-server"

	@syspip install -e ${PWD}
	@echo "You might need to run the following: "
	@echo "  ln -s /Library/Frameworks/Python.framework/Versions/2.7/bin/file_server /usr/local/bin/"

.PHONY: done
done:
	@echo ""
	@echo "File-server Setup Complete"











