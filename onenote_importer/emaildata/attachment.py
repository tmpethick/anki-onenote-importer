# -*- coding: utf-8 -*-
"""
This file is part of the emaildata package
Copyrighted by Karel Antonio Verdecia Ortiz <kverdecia@gmail.com>
License: LGPLv3 (http://www.gnu.org/licenses/lgpl.html)
"""
__docformat__ = "restructuredtext es"
__author__ = "Karel Antonio Verdecia Ortiz"
__contact__ = "kverdecia@gmail.com"

import email
import email.header
from .text import Text


class Attachment(object):
    """Class for extracting attachments from email messages.
    """

    @staticmethod
    def extract(message, only_with_filename=True):
        """
        Iterates by the attachments of the message.

        Parameters
        ----------
        message: email.message.Message
            Message to decode.
        only_only_with_filename: bool
            If its value is `True` (the default) returns only the attachments that have
            a file name. If `False` returns al the attachments.

        Returns
        -------
        attachments: iterator of str
            Iterator with the attachments. Each item in the iterator is a 4 element tuple
            with the decoded content, the filename, the mimetype and a message object if
            the attachment is multipart of `None` if its not.

        Raises
        ------
        TypeError
            If the parameter is not an instance of :class:`email.message.Message`.
        """
        if not isinstance(message, email.message.Message):
            raise TypeError("Expected a message object.")
        if message.is_multipart():
            for attachment in message.get_payload():
                if attachment.is_multipart() and attachment.get_content_type() == 'multipart/alternative':
                    for item in Attachment.extract(attachment, only_with_filename):
                        yield item
                    continue
                if not only_with_filename or attachment.get_filename():
                    try:
                        content = str(attachment) if attachment.is_multipart() else Text.decode_content(attachment)
                        filename = Attachment.decode_filename(attachment.get_filename())
                        mimetype = attachment.get_content_type()
                        yield content, filename, mimetype, attachment
                    except (UnicodeDecodeError, UnicodeEncodeError):
                        continue

    @staticmethod
    def decode_filename(filename):
        if not filename:
            return filename

        def decode(text, encoding):
            """Decode a text. If an exception occurs when decoding returns the
            original text"""
            if encoding is None:
                return text
            try:
                return text.decode(encoding)
            except UnicodeDecodeError:
                return text
        # filename = filename.replace('\n', ' ')
        try:
            pieces = email.header.decode_header(filename)
            pieces = [decode(text, encoding) for text, encoding in pieces]
            return u"".join(pieces).strip()
        except (UnicodeDecodeError, UnicodeEncodeError):
            return filename


