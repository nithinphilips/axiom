.PHONY: all dist install installer

WINPYTHON=C:/Python34/python.exe
PYINSTALLER=C:/Python34/Scripts/pyinstaller.exe
NOSETESTS=C:/Python34/Scripts/nosetests.exe

VERSION := $(shell $(WINPYTHON) dev/extractversion.py)

PRODUCT_NAME=axiom

PRODUCT_GUID=8b9f33d7-fca6-4c7c-bb42-5f59ebca3efd
SOURCEDIR=$(PRODUCT_NAME)
SOURCES := $(shell find $(SOURCEDIR) -iname '*.py')

%.docx: %.rst
	pandoc -t docx -o $@ $<

all: dist/$(PRODUCT_NAME).exe

dist: dist/$(PRODUCT_NAME)-$(VERSION).zip installer
	cp windows/$(PRODUCT_NAME)-$(VERSION).msi dist/

dist/$(PRODUCT_NAME).exe: $(PRODUCT_NAME)-runner.py $(SOURCES) ChangeLog.docx README.docx
	$(PYINSTALLER) --noconfirm axiom.spec
	-cp $(SOURCEDIR)/data/*.* dist/
	cp ChangeLog.docx dist/
	cp README.docx dist/
	cp COPYING dist/

dist/$(PRODUCT_NAME)-$(VERSION).zip: dist/$(PRODUCT_NAME).exe software/instantclient_11_2/
	cd dist; 7z a -y $(PRODUCT_NAME)-$(VERSION).zip . -x!*.zip

install:
	$(WINPYTHON) setup.py install

installer: dist/$(PRODUCT_NAME).exe
	VERSION=$(VERSION) PRODUCT_GUID=$(PRODUCT_GUID) PRODUCT_NAME=$(PRODUCT_NAME) $(MAKE) -C windows

clean:
	rm -rf *.egg-info/ build/
	rm -f README.docx ChangeLog.docx
	VERSION=$(VERSION) $(MAKE) -C windows clean
	find . | grep -E '(__pycache__|\.pyc|\.pyo)' | xargs rm -rf

distclean:
	rm -rf dist

test:
	$(NOSETESTS)

