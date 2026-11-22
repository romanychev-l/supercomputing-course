.PHONY: check latex practice practice-serial
check:
	python3 tools/check_materials.py
latex:
	$(MAKE) -C 08_LaTeX all
practice-serial:
	$(MAKE) -C 06_Практикум serial
	python3 06_Практикум/Инструменты/verify.py --serial-only
practice:
	$(MAKE) -C 06_Практикум check
