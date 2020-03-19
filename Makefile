default:
	./orgviz.py 

docs:
	./orgviz.py --profilePictures --profilePictureDirectory examples/profilePics/ -T png -I examples/ExampleCompany.org --dpi 300
	mv orgviz.png docs/ExampleCompany.png 
	asciidoctor README.adoc

.PHONY: docs default
