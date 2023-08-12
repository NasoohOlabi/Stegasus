# Stegasus

[![Open In Colab](https://raw.githubusercontent.com/NasoohOlabi/Stegasus/f26a918876e2561fc45f7a90c4fa0386ab76608b/ColabBadge.svg)](https://colab.research.google.com/github/NasoohOlabi/Stegasus/blob/main/Stegasus.ipynb)

A Multi-Phase Steganography Engine Using Typos, Synonyms and Emoticons.
We all make misstakes and roll on the floor laughing 🤣🤣🤣.

## Notes

 Still in early dev...

## Links

 [Report Paper](https://docs.google.com/document/d/12p-etkNhbgijaJc5Wds4g9J6etcsgQcYH39K8qP0Kz4/edit?usp=sharing) also almost 50% is done

 [Report Slides](https://docs.google.com/presentation/d/1jGV2UGp9pTdRHHqymk1Tppx5bz2L-U-Dt_y0wYrc2ts/edit?usp=sharing) Reflects current work!

 [Typoceros](https://github.com/NasoohOlabi/Typoceros) The Typo Engine.

## Still in Development

- [X] Migrate Typoceros to java to solve the lang_tool bottle neck
- [X] Double check masked stego no name changing!
- [X] Decode Emojier
- [X] use extract_pos masking. issue: emoticons appear after and which doesn't make since!
- [X] Try make Emoji multiplicity reach 3.
- [X] Try add 👍 Emoji since it's missing in labels.
- [X] help Emojier after you shot it in the head with the last commit cutting ticks in half
- [ ] Benchmarks and Demo.
  - [ ] Tune Emojier and Typoceros on high capacity then low capacity.
  - [ ] Try each setting on the same chat.
  - [ ] Pick low
  - [ ] Try on a large chat dataset.
  - [ ] benchmark without compression.
- [ ] first layer should be chat aware!
- [X] package it
