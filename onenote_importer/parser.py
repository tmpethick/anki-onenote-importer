import os
import mimetypes
import urlparse
import email
from datetime import datetime
from tempfile import NamedTemporaryFile

from BeautifulSoup import BeautifulSoup
from emaildata.text import Text
from emaildata.attachment import Attachment


class Parser(object):
    def __init__(self, file_path):
        with open(file_path) as file_:
            self.message = email.message_from_file(file_)
        html, content_location = Text.html(self.message)
        url = urlparse.urlparse(content_location)
        self.root = os.path.dirname(url.path)
        self.soup = BeautifulSoup(html)
        self.date_hash = datetime.today().strftime("%Y-%m-%d-%H-%M-%S_")
        self.file_map = {}

    def run(self):
        # Create a file for every image found in the .mht.
        for content, filename, mimetype, message\
                in Attachment.extract(self.message, False):

            extension = mimetypes.guess_extension(mimetype)

            # The .mht onenote export contains a .htm file with the content
            # and a .xml file with path structure. Ignore these.
            if extension in ['.htm', '.xml']:
                continue

            # Create a unique filename
            url = message.get('Content-Location')
            path = urlparse.urlparse(url).path
            path = os.path.normpath(path)
            filename = os.path.basename(path)
            filename = self.date_hash + filename

            # Don't create if a similar file is already saved
            if self.file_map.get(path):
                continue

            # Create a temp file which is later moved to the collection.media
            # folder. `filename` is the name it will eventually be called.
            with NamedTemporaryFile(suffix=filename, delete=False) as file_:
                file_.write(content)
                self.file_map[path] = {
                    'filename': filename,
                    'path': file_.name,
                }

        # Replace `src` on every image so it works in Anki.
        for img in self.soup.findAll('img'):
            path = self._get_absolute_path_from_relative_path(img.get('src'))
            path = os.path.normpath(path)
            new_src = self.file_map.get(path).get('filename')
            img['src'] = new_src

            # Make sure it stretches in anki on resizing
            img['width'] = 'auto'
            img['height'] = 'auto'

        # Build the format that the Anki importer can parse.
        output = ''
        table = self.soup.find('table')
        for row in table.findAll('tr'):
            tds = [td for td in row.findAll(recursive=False, limit=2)]
            question = self._strip_newlines(tds[0].renderContents())
            answer = self._strip_newlines(tds[1].renderContents())
            output += '%s\t%s\n' % (question, answer)
        return output

    def _get_absolute_path_from_relative_path(self, relative_path):
        return os.path.join(self.root, relative_path)

    def _strip_newlines(self, string):
        return string.replace('\n', '').replace('\r', '')
