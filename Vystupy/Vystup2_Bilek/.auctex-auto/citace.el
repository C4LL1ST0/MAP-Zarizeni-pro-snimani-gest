;; -*- lexical-binding: t; -*-

(TeX-add-style-hook
 "citace"
 (lambda ()
   (LaTeX-add-bibitems
    "prehled-NN"
    "af"
    "LSTM"
    "dense"
    "loss"
    "optim"
    "percp"))
 '(or :bibtex :latex))

