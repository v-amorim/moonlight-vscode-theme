VSCE_DIR := src/extension

package:
	cd $(VSCE_DIR) && vsce package

publish:
	cd $(VSCE_DIR) && vsce publish
