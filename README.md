# Stegasus

[![Open In Colab](ColabBadge.svg)](https://colab.research.google.com/github/NasoohOlabi/Stegasus/blob/main/Stegasus.ipynb)

A Multi-Phase Steganography Engine Using Typos, Synonyms and Emoticons.
We all make misstakes and roll on the floor laughing 🤣🤣🤣.

## Notes

 Still in early dev

 [Report Paper](https://docs.google.com/document/d/12p-etkNhbgijaJc5Wds4g9J6etcsgQcYH39K8qP0Kz4/edit?usp=sharing) also in early writing 😅

## Still in Development

- [X] Migrate Typoceros to java to solve the lang_tool bottle neck
- [X] Double check masked stego no name changing!
- [X] Decode Emojier
- [X] use extract_pos masking. issue: emoticons appear after and which doesn't make since!
- [ ] Try make Emoji multiplicity reach 3.
- [ ] Try add 👍 Emoji since it's missing in labels.
- [ ] add setting to activate Emojier on %25 percent of the time instead of %50 present.
- [ ] Benchmarks and Demo.
  - [ ] Tune Emojier and Typoceros on high capacity then low capacity.
  - [ ] Try each setting on the same chat.
  - [ ] Pick low
  - [ ] Try on a large chat dataset.
  - [ ] benchmark without compression.
