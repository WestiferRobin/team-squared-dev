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
	  '  make setup                   Initialize approved child pins and parent config; no child setup' \
	  '  make sync                    Sync clean parent master to approved pins; not feature updates' \
	  '  make scaffold-service SERVICE=<service> DOMAIN=<Domain>  DEFERRED: older generator; not onboarding' \
	  '    Repair before generating another service; do not scaffold existing User.' \
	  '' 'FULL STACK (build/run/migrate/smoke currently blocked)'  \
	  '  make build [ENV=local|dev]    BLOCKED: incomplete parent runtime composition' \
	  '  make run [ENV=local|dev]      BLOCKED: use standalone child guides' \
	  '  make stop [ENV=local|dev]     Stop only this box; preserve volumes' \
	  '  make logs [ENV=local|dev]     Follow aggregate stack logs' \
	  '  make migrate [ENV=local|dev]  BLOCKED: incomplete backend migration contract' \
	  '' 'VERIFY' \
	  '  make test                    Delegate normal ACTIVE child tests; app E2E remains off' \
	  '  make smoke [ENV=local|dev]    BLOCKED: incomplete parent runtime contract' \
	  '' 'ENV defaults to local. LOCAL: developer containers. DEV: built verification containers.' \
	  'First use: make setup, then follow the selected child README.' \
	  'Root make test delegates child suites; parent tooling tests are documented separately.' \
	  'Active contracts must be complete before the box can build or run.' \
	  'goalstats-user-service runtime contract pending; references and docs are non-runtime.' \
	  'See README.md, docs/CONTRIBUTING.md and docs/READINESS.md.'
	@bash scripts/box.sh list
setup sync:
	@bash scripts/workspace.sh "$@"

build run stop logs migrate test smoke:
	@bash scripts/box.sh "$@" "$${ENV}" "$${PROJECT}"

scaffold-service:
	@bash scripts/scaffold-service.sh
