c:\Python24\python.exe c:\Python24\scripts\rst2html.py --stylesheet-path=style.css --embed-stylesheet why_stackless.txt why_stackless.html

c:\Python24\python.exe c:\Python24\scripts\rst2latex.py why_stackless.txt --stylesheet=style.tex --documentclass=book --documentoptions=10pt,letter why_stackless.latex
latex why_stackless.latex 
dvipdfm why_stackless.dvi 

del why_stackless.aux why_stackless.latex why_stackless.dvi why_stackless.log why_stackless.out
