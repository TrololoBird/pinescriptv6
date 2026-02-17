.PHONY: check check-dev contract-check lint style-check contract-init

check:
	python tools/contract_guard.py --check && python tools/lint_guard.py

check-dev:
	python tools/lint_guard.py

contract-check:
	python tools/contract_guard.py --check

lint:
	python tools/lint_guard.py

style-check:
	python tools/diff_scope_guard.py --mode=style-only

contract-init:
	python tools/contract_guard.py --init
