mkdir invoice-tool
for f in .[!.]* *; do [ "$f" = invoice-tool ] || mv "$f" invoice-tool/; done
