.PHONY: all clean

CANDLE=candle
LIGHT=light

PRODUCT_NAME ?= something
# Version is normally set from the parent Makefile
VERSION ?= 0.0.0
# Increment the GUID for each release
PRODUCT_GUID ?= NONE

%-$(VERSION).wixobj: %.wxs
	# Build Object file
	$(CANDLE) -nologo -out $@ $< -dVERSION=$(VERSION) -dPRODUCTGUID=$(PRODUCT_GUID)

%.msi: %.wixobj
	# Build MSI
	$(LIGHT) -ext WixUIExtension -out $@ -nologo $<

$(PRODUCT_NAME)-$(VERSION).msi: ../dist/$(PRODUCT_NAME).exe

all: $(PRODUCT_NAME)-$(VERSION).msi

debug: $(PRODUCT_NAME)-$(VERSION).msi
	msiexec /i $(PRODUCT_NAME)-$(VERSION).msi /L*v  $(PRODUCT_NAME)-$(VERSION)_debug.log

clean:
	-rm -f *.msi *.wixobjs *.wixpdb

