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
import cStringIO
import mimetools


class Text(object):
    """Utility class for decoding content of messages, convert text enconding to utf-8 and
    extracting text of html from messages.
    """
    @staticmethod
    def decode_content(message):
        """Decode the content of a message. This method do not checks if the message is
        multipart or if the message mime type is plain text or html.

        Parameters
        ----------
        message: email.message.Message
            Message to decode.

        Returns
        -------
        content: str
            Decoded content of the message

        Raises
        ------
        TypeError
            If the parameter is not an instance of :class:`email.message.Message`.
        """
        if not isinstance(message, email.message.Message):
            raise TypeError("Expected a message object.")
        encoding = message['Content-Transfer-Encoding']
        if encoding and encoding.strip() == 'quoted-printable':
            result = message.get_payload()
            stream = cStringIO.StringIO(result)
            output = cStringIO.StringIO()
            mimetools.decode(stream, output, 'quoted-printable')
            return output.getvalue()
        return message.get_payload(decode=True)

    @staticmethod
    def decode_text(message):
        """Extracts the text of the message and try to convert it to utf-8. This method
        do not checks if the message is multipart or if the message mime type is plain
        text or html. Maybe you want to use the methods :class:`Text.text` and
        :class:`Text.html`.

        Parameters
        ----------
        message: email.message.Message
            Message to extract its text.

        Returns
        -------
        content: str
            Text of the message encoded to utf-8. If it cannot encode the text to utf-8
            the text will be returned as ascii.

        Raises
        ------
        TypeError
            If the parameter is not an instance of :class:`email.message.Message`.
        """
        def utf8(text):
            try:
                charset = message.get_content_charset()
                if charset:
                    return text.decode(charset).encode('utf-8')
            except LookupError:
                return text
            except (UnicodeDecodeError, UnicodeEncodeError):
                return text
            return text
        try:
            return utf8(Text.decode_content(message))
        except (UnicodeDecodeError, UnicodeEncodeError):
            return message.get_payload().encode('ascii')

    @staticmethod
    def decoded(message, allowed_mimetypes=None):
        """
        If the mimetype of the message is in the `allowed_mimetypes` parameter returns
        returns its content decoded. If the message is multipart find in the attachments
        a message with mimetype in the `allowed_mimetypes` parameter and returns its
        content decoded.

        Parameters
        ----------
        message: email.message.Message
            Message to decode.
        allowed_mimetypes: iterable
            Iterable object with the mimetypes will be used the select the message to
            extract its text. Only `text/plain` and `text/html` allowed or a
            `ValueError` exception will be raised.

        Returns
        -------
        message_text: str
            Returns the plain text of the message. This method will try return the text
            encoded to `utf-8`. If it can't, returns it with its original encoding. If
            it can't find the text returns `None`.

        Raises
        ------
        TypeError
            If the parameter is not an instance of :class:`email.message.Message`.
        ValueError
            If the value in the parameter allowed_mimetypes is incorrect.
        """
        if allowed_mimetypes is None:
            allowed_mimetypes = ('text/plain', 'text/html')
        wrong_mime_types = frozenset(allowed_mimetypes).difference(['text/plain', 'text/html'])
        if wrong_mime_types:
            raise ValueError("Wrong mime types: {0}".format(list(wrong_mime_types)))
        if not isinstance(message, email.message.Message):
            raise TypeError("Expected a message object.")
        if not message.is_multipart():
            if message.get_filename():
                return None
            if message.get_content_type() in allowed_mimetypes:
                return (Text.decode_text(message), 
                    message.get('Content-Location'))
            return None
        for sub_message in message.get_payload():
            if not sub_message.is_multipart() or sub_message.get_content_type() == 'multipart/alternative':
                result = Text.decoded(sub_message)
                if result:
                    return result
        return None

    @staticmethod
    def text(message):
        """Returns the plain text of the message. If the message is multipart search
        for an attachment with no filename and with mimetype `text/plain` and returns
        it.

        Parameters
        ----------
        message: email.message.Message
            Message to decode.

        Returns
        -------
        message_text: str
            Returns the plain text of the message. This method will try return the text
            encoded to `utf-8`. If it can't, returns it with its original encoding. If
            it can't find the text returns `None`.

        Raises
        ------
        TypeError
            If the parameter is not an instance of :class:`email.message.Message`.
        """
        return Text.decoded(message, ['text/plain'])

    @staticmethod
    def html(message):
        """Returns the html of the message. If the message is multipart search for an
        attachment with no filename and with mimetype `text/html` and returns it.

        Parameters
        ----------
        message: email.message.Message
            Message to decode.

        Returns
        -------
        message_text: str
            Returns the html of the message. This method will try return the html
            encoded to `utf-8`. If it can't, returns it with its original encoding. If
            it can't find the text returns `None`.

        Raises
        ------
        TypeError
            If the parameter is not an instance of :class:`email.message.Message`.
        """
        return Text.decoded(message, ['text/html'])

    @staticmethod
    def undecoded(message, allowed_mimetypes=None):
        """This method is similar to :class:`Text.decoded` but it doesn't try to decode the
        returned text.
        """
        if allowed_mimetypes is None:
            allowed_mimetypes = ('text/plain', 'text/html')
        wrong_mime_types = frozenset(allowed_mimetypes).difference(['text/plain', 'text/html'])
        if wrong_mime_types:
            raise ValueError("Wrong mime types: {0}".format(list(wrong_mime_types)))
        if not isinstance(message, email.message.Message):
            raise TypeError("Expected a message object.")
        if not message.is_multipart():
            if message.get_filename():
                return None
            if message.get_content_type() in allowed_mimetypes:
                return message.get_payload()
            return None
        for sub_message in message.get_payload():
            if not sub_message.is_multipart() or sub_message.get_content_type() == 'multipart/alternative':
                result = Text.undecoded(sub_message)
                if result:
                    return result
        return None

    @staticmethod
    def undecoded_text(message):
        """
        This method is similar to :class:`Text.text` but it doesn't try to decode the
        returned text.
        """
        return Text.undecoded(message, ['text/plain'])

    @staticmethod
    def undecoded_html(message):
        """
        This method is similar to :class:`Text.html` but it doesn't try to decode the
        returned text.
        """
        return Text.undecoded(message, ['text/html'])
