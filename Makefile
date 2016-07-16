# -*- Makefile for file_server files -*-
# Copyright 2013 Saevon <saevon.kyomae@gmail.com>
# TODO: install completions file?

.PHONY: all
all: main completion done

.PHONY: main
main:
	@echo "Setting up file-server"

	@pip install -e .

.PHONY: done
done:
	@echo ""
	@echo "File-server Setup Complete"


.PHONY: completion
completion:
	@ln -i -s ${PWD}/*.complete.bash ${HOME}/.bash_completion.d/ || true











