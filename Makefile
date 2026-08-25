PYTHON ?= python3

.PHONY: bootstrap-data audit check data-check static-check smoke

bootstrap-data:
	$(PYTHON) scripts/bootstrap_upstream.py

audit:
	$(PYTHON) scripts/audit_jp_zh_homographs.py

check:
	$(PYTHON) scripts/audit_public_artifacts.py
	$(PYTHON) scripts/validate_repository.py

data-check:
	$(PYTHON) scripts/audit_public_artifacts.py

static-check:
	PYTHONPYCACHEPREFIX=/tmp/doppelganger-jc-pycache $(PYTHON) -m compileall -q scripts

smoke:
	$(PYTHON) scripts/smoke_test.py
