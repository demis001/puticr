.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	rm -rf puticr/download
	rm -rf puticr/bin
	rm -rf puticr/lib
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -rf {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	.  puticr/bin/activate && \
	flake8 puticr tests

test: ## run tests quickly with the default Python
	
	py.test

test-all: ## run tests on every Python version with tox
	. puticr/bin/activate && \
	tox

coverage: ## check code coverage quickly with the default Python
	. puticr/bin/activate && \
	coverage run --source puticr -m pytest && \
	coverage report -m && \
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/puticr.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ puticr
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	    command -v virtualenv > /dev/null 2>&1 || pip install virtualenv --user
		virtualenv puticr && \
		. puticr/bin/activate && \
		pip install -U Paver && \
		pip install -r requirements_dev.txt && \
		pip install -U sphinx_rtd_theme && \
		mkdir -p puticr/download && \
		mkdir -p puticr/files && \
	    python setup.py install && \
		cp puticr/cgmaptools puticr/bin && \
		cp puticr/update_CGmap2.py puticr/bin && \
		cp puticr/identify_hotspot_V2.py puticr/bin && \
		cd puticr/bin && ln -sf ../download/BSseeker2/Antisense.py Antisense.py && \
		ln -sf ../download/BSseeker2/bs_seeker2-align.py bs_seeker2-align.py && \
		ln -sf ../download/BSseeker2/bs_seeker2-build.py bs_seeker2-build.py && \
		ln -sf ../download/BSseeker2/bs_seeker2-call_methylation.py bs_seeker2-call_methylation.py && \
		ln -sf ../download/BSseeker2/FilterReads.py FilterReads.py && \
		ln -sf  ../download/cgmaptools-0.1.2/src/ASM.pl ASM && \
		ln -sf  ../download/cgmaptools-0.1.2/src/ATCGmapCovInBins.py ATCGmapCovInBins && \
		ln -sf  ../download/cgmaptools-0.1.2/src/ATCGmapStatCov.py ATCGmapStatCov  && \
		ln -sf  ../download/cgmaptools-0.1.2/src/ATCGmapToCGmapWig.py ATCGmapToCGmapWig  && \
		ln -sf  ../download/cgmaptools-0.1.2/src/BismarkToCGmap.py BismarkToCGmap  && \
		ln -sf  ../download/cgmaptools-0.1.2/src/CGmapCovInBins.py CGmapCovInBins  && \
		ln -sf  ../download/cgmaptools-0.1.2/src/CGmapFillContext.py CGmapFillContext  && \
		ln -sf  ../download/cgmaptools-0.1.2/src/CGmapFillIndex.py CGmapFillIndex  && \
		ln -sf  ../download/cgmaptools-0.1.2/src/CGmapInterDiffReg.py CGmapInterDiffReg  && \
		ln -sf  ../download/cgmaptools-0.1.2/src/CGmapInterDiffSite.py CGmapInterDiffSite  && \
		ln -sf  ../download/cgmaptools-0.1.2/src/CGmapIntersect.py CGmapIntersect  && \
		ln -sf  ../download/cgmaptools-0.1.2/src/CGmapMerge.py CGmapMerge && \
		ln -sf  ../download/cgmaptools-0.1.2/src/CGmapMethInBins.py CGmapMethInBins && \
		ln -sf  ../download/cgmaptools-0.1.2/src/CGmapSelectBySite.py CGmapSelectBySite && \
		ln -sf  ../download/cgmaptools-0.1.2/src/CGmapsMethInBins.py CGmapsMethInBins && \
		ln -sf  ../download/cgmaptools-0.1.2/src/CGmapSplitByChr.py CGmapSplitByChr && \
		ln -sf  ../download/cgmaptools-0.1.2/src/CGmapStatCov.py CGmapStatCov && \
		ln -sf  ../download/cgmaptools-0.1.2/src/CGmapStatMeth.py CGmapStatMeth && \
		ln -sf  ../download/cgmaptools-0.1.2/src/CGmapToRegion.py CGmapToRegion && \
		ln -sf  ../download/cgmaptools-0.1.2/src/CGmapToWig.py CGmapToWig && \
		ln -sf  ../download/cgmaptools-0.1.2/src/FindCCGG.py FindCCGG && \
		ln -sf  ../download/cgmaptools-0.1.2/src/FragRegFromBED.py FragRegFromBED && \
		ln -sf  ../download/cgmaptools-0.1.2/src/mCBinHeatmap.R mCBinHeatmap && \
		ln -sf  ../download/cgmaptools-0.1.2/src/mCFragRegView.R mCFragRegView && \
		ln -sf  ../download/cgmaptools-0.1.2/src/mCLollipop.R mCLollipop && \
		ln -sf  ../download/cgmaptools-0.1.2/src/mCTanghulu.pl mCTanghulu && \
		ln -sf  ../download/cgmaptools-0.1.2/src/MergeListOfCGmap.py MergeListOfCGmap && \
		ln -sf  ../download/cgmaptools-0.1.2/src/SNVFromATCGmap.py SNVFromATCGmap && \
		ln -sf  ../download/cgmaptools-0.1.2/src/Sort_chr_pos.py Sort_chr_pos




