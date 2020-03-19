default:
	./orgviz.py 

docs:
	./orgviz.py --profilePictures --profilePictureDirectory examples/profilePics/ -T png -I examples/ExampleCompany.org
	mv orgviz.png docs/ExampleCompany.png 
	asciidoctor README.adoc

.PHONY: docs default
