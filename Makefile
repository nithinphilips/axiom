.PHONY: all dist install installer

# Axiom has to be built with Windows python
PYTHON=C:/Python34/python.exe
PYINSTALLER=C:/Python34/Scripts/pyinstaller.exe
NOSETESTS=C:/Python34/Scripts/nosetests.exe
PANDOC=pandoc
GIT=git

PRODUCT_NAME=axiom
VERSION := $(shell $(PYTHON) dev/extractversion.py)

# Random UUID for each build
PRODUCT_GUID=$(shell uuidgen)

SOURCEDIR=$(PRODUCT_NAME)
SOURCES := $(shell find $(SOURCEDIR) -iname '*.py')

# Distribution folder and distribution zip file name
DISTROOT=./dist
DISTDIR=$(PRODUCT_NAME)-$(VERSION)
DISTZIP=$(PRODUCT_NAME)-$(VERSION).zip
SRCDISTZIP=$(PRODUCT_NAME)-$(VERSION)-src.zip

%.docx: %.rst
	$(PANDOC) -t docx -o $@ $<

all: ChangeLog.docx README.docx $(DISTROOT)/$(PRODUCT_NAME).exe $(DISTROOT)/$(PRODUCT_NAME)-parser.exe

$(DISTROOT)/$(PRODUCT_NAME)-parser.exe: $(PRODUCT_NAME)-parser-runner.py axiom-parser.spec $(SOURCES)
	$(PYINSTALLER) --noconfirm axiom-parser.spec

$(DISTROOT)/$(PRODUCT_NAME).exe: $(PRODUCT_NAME)-runner.py axiom.spec $(SOURCES)
	$(PYINSTALLER) --noconfirm axiom.spec
	-cp $(SOURCEDIR)/data/*.* dist/

$(DISTROOT)/$(DISTZIP): $(DISTROOT)/$(PRODUCT_NAME).exe $(DISTROOT)/$(PRODUCT_NAME)-parser.exe
	rm -rf $(DISTROOT)/$(DISTDIR)
	mkdir -p $(DISTROOT)/$(DISTDIR)
	cp dist/$(PRODUCT_NAME).exe $(DISTROOT)/$(DISTDIR)
	cp dist/$(PRODUCT_NAME)-parser.exe $(DISTROOT)/$(DISTDIR)
	-cp $(SOURCEDIR)/data/*.* dist/
	cp *.docx $(DISTROOT)/$(DISTDIR)
	cp COPYING $(DISTROOT)/$(DISTDIR)
	cd $(DISTROOT) && zip -r $(DISTZIP) $(PRODUCT_NAME)-$(VERSION)/
	rm -rf $(DISTROOT)/$(DISTDIR)

install:
	$(PYTHON) setup.py install

installer: $(DISTROOT)/$(PRODUCT_NAME).exe $(DISTROOT)/$(PRODUCT_NAME)-parser.exe
	VERSION=$(VERSION) PRODUCT_GUID=$(PRODUCT_GUID) PRODUCT_NAME=$(PRODUCT_NAME) $(MAKE) -C windows

clean:
	rm -rf *.egg-info/ build/
	rm -f README.docx ChangeLog.docx
	VERSION=$(VERSION) $(MAKE) -C windows clean
	find . | grep -E '(__pycache__|\.pyc|\.pyo)' | xargs rm -rf

dist: all distzip installer distsrc
	cp windows/$(PRODUCT_NAME)-$(VERSION).msi dist/

distclean:
	rm -rf dist

distzip: $(DISTROOT)/$(DISTZIP)

distsrc:
	mkdir -p $(DISTROOT)
	rm -f $(DISTROOT)/$(SRCDISTZIP)
	$(GIT) archive --format zip --output $(DISTROOT)/$(SRCDISTZIP) HEAD

test:
	$(NOSETESTS)
