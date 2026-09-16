# GNU Make 3.81+ and Bash on macOS/Linux.
SHELL := /bin/bash
.DEFAULT_GOAL := help
ENV ?= local
PROJECT ?=
export ENV PROJECT
DRY_RUN ?= false
# Freeze literal command-line values; never expand user Make expressions.
override SERVICE := $(value SERVICE)
override DOMAIN := $(value DOMAIN)
override DRY_RUN := $(value DRY_RUN)
export SERVICE DOMAIN DRY_RUN
.PHONY: help setup sync scaffold-service build run stop logs migrate test smoke
help:
	@printf '%s\n' \
	  'Canonical workspace: edit independent child repositories directly.' \
	  'WORKSPACE' \
	  '  make help                    Show scope and commands' \
	  '  make setup                   Prepare this checkout and missing env files; no Docker' \
	  '  make sync                    Fast-forward parent master; synchronize approved pins; no Docker' \
	  '  make scaffold-service SERVICE=<service> DOMAIN=<Domain>  Transform pinned Flask identity (Python 3.12)' \
	  '    Safe pinned detached/master destination; actual attaches to master.' \
	  '' 'FULL STACK' \
	  '  make build [ENV=local|dev]    Build every active image' \
	  '  make run [ENV=local|dev]      Start one box; wait for required readiness' \
	  '  make stop [ENV=local|dev]     Stop only this box; preserve volumes' \
	  '  make logs [ENV=local|dev]     Follow aggregate stack logs' \
	  '  make migrate [ENV=local|dev]  Run active child migration tooling against box databases' \
	  '' 'VERIFY' \
	  '  make test                    Delegate normal ACTIVE child tests; app E2E remains off' \
	  '  make smoke [ENV=local|dev]    Check the running box and internal connectivity' \
	  '' 'ENV defaults to local. LOCAL: developer containers. DEV: built verification containers.' \
	  'First use: make setup. Runtime later: make migrate; make run.' \
	  'DRY_RUN=true previews with no writes. DOMAIN changes identity, never Item/Action.' \
	  'Active contracts must be complete before the box can build or run.' \
	  'goalstats-user-service runtime contract pending; references and docs are non-runtime.' \
	  'See docs/READINESS.md and docs/DEVELOPMENT.md.'
	@bash scripts/box.sh list
setup sync:
	@bash scripts/workspace.sh "$@"

build run stop logs migrate test smoke:
	@bash scripts/box.sh "$@" "$${ENV}" "$${PROJECT}"

scaffold-service:
	@bash scripts/scaffold-service.sh
