import shutil
from tempfile import mkdtemp

import aqt
from aqt import mw
from aqt.qt import *
from aqt.utils import getFile, showText
from anki.importing import TextImporter

import ui
from parser import Parser


class MHTImportDialog(QDialog):
    def __init__(self, mw, importer):
        QDialog.__init__(self, mw, Qt.Window)
        self.mw = mw
        self.importer = importer
        self.frm = ui.Ui_MHTImportDialog()
        self.frm.setupUi(self)

        b = QPushButton(_("Import"))
        self.frm.buttonBox.addButton(b, QDialogButtonBox.AcceptRole)

        self.deck = aqt.deckchooser.DeckChooser(
            self.mw, self.frm.deckArea, label=False)

        self.exec_()

    def accept(self):
        self.importer.importMode = 1
        self.mw.pm.profile['importMode'] = self.importer.importMode

        self.importer.allowHTML = True
        self.mw.pm.profile['allowHTML'] = self.importer.allowHTML

        did = self.deck.selectedId()
        if did != self.importer.model['did']:
            self.importer.model['did'] = did
            self.mw.col.models.save(self.importer.model)
        self.mw.col.decks.select(did)

        self.mw.progress.start(immediate=True)
        self.mw.checkpoint(_("Import"))

        self.importer.run()

        self.mw.progress.finish()
        txt = _("Importing complete.") + "\n"
        if self.importer.log:
            txt += "\n".join(self.importer.log)
        self.close()
        showText(txt)
        self.mw.reset()


def importMHT():
    # Ask for the .mht file.
    file_path = getFile(mw, _("Import mht file"), None, key="import")
    if not file_path:
        return
    file_path = unicode(file_path)

    # Convert mht
    parser = Parser(file_path)
    output = parser.run()

    # Creates a temp dir instead of file since windows
    # won't allow subprocesses to access it otherwise.
    # https://stackoverflow.com/questions/15169101/how-to-create-a-temporary-file-that-can-be-read-by-a-subprocess
    try:
        temp_dir = mkdtemp()
        path = os.path.join(temp_dir, 'import.html')

        with open(path, 'w+') as html:
            html.write(output)
            # Move temp images to collection.media
            media_dir = os.path.join(mw.pm.profileFolder(), "collection.media")

            for meta in parser.file_map.values():
                temp_path = meta.get('path')
                new_path = os.path.join(media_dir, meta.get('filename'))
                shutil.move(temp_path, new_path)

        # import into the collection
        ti = TextImporter(mw.col, path)
        ti.delimiter = '\t'
        ti.allowHTML = True
        ti.initMapping()
        MHTImportDialog(mw, ti)

        # Remove file
        os.remove(path)
    finally:
        os.rmdir(temp_dir)


action = QAction("Import mht...", mw)
mw.connect(action, SIGNAL("triggered()"), importMHT)
mw.form.menuTools.addAction(action)
