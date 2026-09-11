# GNU Make 3.81+ and Bash on macOS/Linux.
SHELL := /bin/bash
.DEFAULT_GOAL := help
ENV ?= local
PROJECT ?=
export ENV PROJECT
.PHONY: help setup build run stop logs migrate test smoke
help:
	@printf '%s\n' \
	  'These commands operate the complete ACTIVE Team Squared development box.' \
	  'SETUP' \
	  '  make help                    Show scope and commands' \
	  '  make setup                   Check tools, initialize committed pins, preserve configuration' \
	  '' 'BUILD / RUN' \
	  '  make build [ENV=local|dev]    Build every active image' \
	  '  make run [ENV=local|dev]      Start one box; wait for required readiness' \
	  '  make stop [ENV=local|dev]     Stop only this box; preserve volumes' \
	  '  make logs [ENV=local|dev]     Follow aggregate stack logs' \
	  '' 'DATABASE' \
	  '  make migrate [ENV=local|dev]  Run active child migration tooling against box databases' \
	  '' 'TEST / VERIFY' \
	  '  make test                    Delegate normal ACTIVE child tests; app E2E remains off' \
	  '  make smoke [ENV=local|dev]    Check the running box and internal connectivity' \
	  '' 'ENV defaults to local. LOCAL: developer containers. DEV: built verification containers.' \
	  'First use: make setup; make migrate; make run (add ENV=dev for DEV).' \
	  'Children remain independent: cd into an active child and use make help.' \
	  'Active contracts must be complete before the box can build or run.' \
	  'goalstats-user-service runtime contract pending; references and docs are non-runtime.' \
	  'See docs/READINESS.md and docs/DEVELOPMENT.md.'
	@bash scripts/box.sh list
setup build run stop logs migrate test smoke:
	@bash scripts/box.sh "$@" "$${ENV}" "$${PROJECT}"
