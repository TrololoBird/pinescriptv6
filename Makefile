.PHONY: check check-dev check-release contract-check contract-dev contract-release lint style-check contract-init tv-export

check: check-dev

check-dev:
	python tools/contract_guard.py --mode dev --check && python tools/lint_guard.py --dev

check-release:
	python tools/contract_guard.py --mode release --check && python tools/lint_guard.py

contract-dev:
	python tools/contract_guard.py --mode dev --check

contract-release:
	python tools/contract_guard.py --mode release --check

contract-check: contract-release

lint:
	python tools/lint_guard.py

style-check:
	python tools/diff_scope_guard.py --mode=style-only

contract-init:
	python tools/contract_guard.py --init


tv-export:
	python tools/tv_export.py
