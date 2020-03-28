default:
	./orgviz.py 

docs:
	./orgviz.py --profilePictures --profilePictureDirectory examples/profilePics/ -T png -I examples/ExampleCompany.org --dpi 300
	mv orgviz.png docs/ExampleCompany.png 
	asciidoctor README.adoc

tests: test
test:
	coverage run --branch --source orgviz -m pytest
	coverage report
	coverage html

tests-debian:
	python-coverage run --branch --source orgviz -m pytest
	python-coverage report
	pyrgon-coverage html

lint:
	pylint-3 orgviz

.PHONY: docs default test 
