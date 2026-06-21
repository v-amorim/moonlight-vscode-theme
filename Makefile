VSCE_DIR := src/extension

package:
	cd $(VSCE_DIR) && vsce package

publish:
	cd $(VSCE_DIR) && vsce publish

schema-check:
	python scripts/update_schema.py

schema-update:
	python scripts/update_schema.py --write
