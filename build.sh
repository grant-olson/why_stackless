#!/bin/sh

#rmdir /S /Q build

#cvs -d:ext:grant@cvs.yoyodyne.gto:/usr/local/cvsroot export -dbuild -DNOW why_stackless

#cd build

mkdir docs

cp style.tex docs/
cp style.css docs/

rst2html --stylesheet-path=style.css --embed-stylesheet why_stackless.txt docs/why_stackless.html

rst2latex why_stackless.txt --use-latex-toc --use-latex-docinfo --stylesheet=style.tex --use-verbatim-when-possible --documentclass=book --no-section-numbering --documentoptions=10pt,letter docs/why_stackless.latex

cd docs

:: run twice to get good Table of Contents
latex why_stackless.latex 
latex why_stackless.latex

dvipdfm why_stackless.dvi 

rm why_stackless.aux why_stackless.dvi why_stackless.log why_stackless.out
rm why_stackless.latex
rm style.css style.tex .cvsignore why_stackless.toc

cd ..

tar cvf docs/why_stackless_code.tar code
gzip docs/why_stackless_code.tar
