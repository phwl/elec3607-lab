%.tex : %.ipynb
	jupyter nbconvert --to markdown $<
	pandoc --listings -f markdown -t latex $*.md -o $@

%.pdf : %.ipynb
	jupyter nbconvert --to pdf $<

clean:
	-rm -rf *.pdf *.md *.tex *_files
