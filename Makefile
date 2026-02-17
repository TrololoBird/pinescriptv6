.PHONY: check check-dev contract-check contract-dev lint style-check contract-init tv-export

check:
	python tools/contract_guard.py --check && python tools/lint_guard.py

check-dev:
	python tools/contract_guard.py --dev-check && python tools/lint_guard.py --dev

contract-dev:
	python tools/contract_guard.py --dev-check

contract-check:
	python tools/contract_guard.py --check

lint:
	python tools/lint_guard.py

style-check:
	python tools/diff_scope_guard.py --mode=style-only

contract-init:
	python tools/contract_guard.py --init


tv-export:
	python tools/tv_export.py
