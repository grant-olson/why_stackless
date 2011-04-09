:: This is really out-of-date (note the use of cvs)
:: I don't have a windows box right now to update it.
:: But didn't want to delete this file in case you need
:: a starting point

rmdir /S /Q build

cvs -d:ext:grant@cvs.yoyodyne.gto:/usr/local/cvsroot export -dbuild -DNOW why_stackless

cd build

c:\Python24\python.exe c:\Python24\scripts\rst2html.py --stylesheet-path=style.css --embed-stylesheet why_stackless.txt why_stackless.html

c:\Python24\python.exe c:\Python24\scripts\rst2mylatex.py why_stackless.txt --use-latex-toc --use-latex-docinfo --stylesheet=style.tex --use-verbatim-when-possible --documentclass=book --no-section-numbering --documentoptions=10pt,letter why_stackless.latex

:: run twice to get good Table of Contents
latex why_stackless.latex 
latex why_stackless.latex

dvipdfm why_stackless.dvi 

del why_stackless.aux why_stackless.dvi why_stackless.log why_stackless.out
del why_stackless.latex
del *.txt
del build.bat style.css style.tex .cvsignore why_stackless.toc

tar cvf why_stackless_code.tar code
gzip why_stackless_code.tar
rmdir /S /Q code
