for file in *.jpeg ; do
	convert "$file" -resize 100 "$file"
done
