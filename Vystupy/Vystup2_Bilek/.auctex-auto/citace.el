;; -*- lexical-binding: t; -*-

(TeX-add-style-hook
 "citace"
 (lambda ()
   (LaTeX-add-bibitems
    "prehled-NN"
    "af"))
 '(or :bibtex :latex))

