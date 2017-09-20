# OneNote importer

This addon can import `.mht` files exported from OneNote. It looks for a table and create a card for every row where the first column is the front side and the second is the back side. Html format and images in the table cells are supported.

## Features
- Able to import multiple tables in one `.mht` file
## Development

To generate ui file:

```
brew install pyqt
pyuic4 anki_importer/importing.ui -x -o anki_importer/ui.py
```
