# Kubrick makefile

deb_version		:= $(shell dpkg-parsechangelog | sed -ne "s/^Version: \(.*\)/\1/p")
upstream_fullname		:= $(shell python setup.py --fullname)
upstream_fullname_fix	:= $(shell python setup.py --fullname | tr \~ \-)
upstream_name			:= $(shell python setup.py --name)
upstream_version		:= $(shell python setup.py --version)
orig			:= $(upstream_name)_$(upstream_version).orig

sdist:
	python setup.py sdist

clean:
	rm -Rf dist build kubrick.egg-info debsource

debsource: sdist
	rm -Rf ./debsource/ && mkdir -p ./debsource/
	cp ./dist/$(upstream_fullname_fix).tar.gz ./debsource/$(orig).tar.gz
	tar xf ./debsource/$(orig).tar.gz -C ./debsource/
	cp -Rf ./debian/ ./debsource/$(upstream_fullname_fix)/
	cd ./debsource/$(upstream_fullname_fix)/ && dpkg-buildpackage -us -uc -S
