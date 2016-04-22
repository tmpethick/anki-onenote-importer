# -*- coding: utf-8 -*-
"""
This file is part of the emaildata package
Copyrighted by Karel Antonio Verdecia Ortiz <kverdecia@gmail.com>
License: LGPLv3 (http://www.gnu.org/licenses/lgpl.html)
"""
__docformat__ = "restructuredtext es"
__author__ = "Karel Antonio Verdecia Ortiz"
__contact__ = "kverdecia@gmail.com"

import datetime
import email
import email.message
import email.header
import email.utils
import re
from charset import text_to_utf8


class MetaData(object):
    """
    Objects of this class extract metadata from email headers.
    """
    re_recieved = re.compile(r'for <(.*@.*)>;')
    re_in_reply_to = re.compile(r"<.*>", re.MULTILINE)

    def __init__(self, message=None):
        """
        Parameters
        ----------
        message: email.message.Message
            Email message from which the metadata will be extracted.
        """
        self.names = dict()
        self.message = None
        self.message_id = None
        self.to = None
        self.sender = None
        self.reply_to = None
        self.cc = None
        self.bcc = None
        self.in_reply_to = None
        self.subject = None
        self.content_type = None
        self.date = None
        self.timestamp = None
        self.received_date = None
        self.received_timestamp = None
        self.charset = None
        self.receivers = None
        if message is None:
            self.clear()
        elif isinstance(message, email.message.Message):
            self.set_message(message)
        else:
            raise TypeError("The message parameter must be an instance of email.message.Message.")

    def clear(self):
        """Clear the `message` attribute and the extracted metadata.
        """
        self.names = dict()
        self.message = None
        self.message_id = None
        self.to = None
        self.sender = None
        self.reply_to = None
        self.cc = None
        self.bcc = None
        self.in_reply_to = None
        self.subject = None
        self.content_type = None
        self.date = None
        self.timestamp = None
        self.received_date = None
        self.received_timestamp = None
        self.charset = None
        self.receivers = None
        
    def to_dict(self):
        return dict(
            names=self.names, message_id=self.message_id,
            to=self.to, sender=self.sender, reply_to=self.reply_to,
            cc=self.cc, bcc=self.bcc, in_replay_to=self.in_reply_to,
            subject=self.subject, content_type=self.content_type,
            date=self.date, timestamp=self.timestamp, 
            received_date=self.received_date,
            received_timestamp=self.received_timestamp,
            charset=self.charset, receivers=self.receivers)

    @property
    def addresses(self):
        """
        Returns a set with the email addresses detected in the message headers.
        """
        result = set()
        if self.sender:
            result.update({self.sender})
        if self.reply_to:
            result.update(set(self.reply_to))
        result.update(self.receivers())
        return result

    def set_message(self, message):
        """
        Change the message assigned to the instance and extract its metadata.

        Parameters
        ----------
        message: email.message.Message
            The new message from which the metadata will be extracted.
        """
        assert isinstance(message, email.message.Message)
        self.message = message
        self.message_id = message['Message-ID']
        self.to = self._address('To')
        senders = self._address('From')
        self.sender = senders[0] if senders else None
        addresses = self._address('Reply-To')
        self.reply_to = addresses[0] if addresses else None
        self.cc = self._address('Cc')
        self.bcc = self._address('Bcc')
        in_replay_to = message['In-Reply-To']
        if in_replay_to:
            items = self.re_in_reply_to.findall(in_replay_to)
            in_replay_to = items[0] if items else in_replay_to
        self.in_reply_to = in_replay_to
        self.subject = self._header_str('Subject')
        self.content_type = message.get_content_type()
        self.date = self._date('Date')
        self.timestamp = self._timestamp('Date')
        self.received_date = self._date('Received-Date')
        self.received_timestamp = self._timestamp('Received-Date')
        self.charset = message.get_charset()
        self.receivers = self._receivers()

    def __getstate__(self):
        """Method for serialize instances of this class."""
        result = dict(self.__dict__)
        result['message'] = None
        return result

    def _get_header(self, header_name):
        """
        Returns the decoded value of the specified header.
        """
        items = email.header.decode_header(self.message[header_name])
        values = []
        for val, enc in items:
            try:
                values.append(val.decode(enc or 'ascii'))
            except UnicodeDecodeError:
                try:
                    values.append(text_to_utf8(val))
                except UnicodeDecodeError:
                    continue
        return ' '.join(values).encode('utf-8')

    def _header_values(self, header_name):
        """
        Returns a list with the values of the specified header.
        """
        header = self.message[header_name]
        if header is None:
            return []
        items = email.header.decode_header(header)
        values = []
        for val, enc in items:
            try:
                values.append(val.decode(enc or 'ascii'))
            except UnicodeDecodeError:
                try:
                    values.append(text_to_utf8(val))
                except UnicodeDecodeError:
                    continue
        try:
            return [val.encode('utf-8') for val in values]
        except UnicodeDecodeError:
            return values

    def _header_str(self, header_name, join_str=' '):
        """
        Returns a string with the values in the specified header concatenated by
        the value in the parameter `join_str`.
        """
        return join_str.join(self._header_values(header_name))

    def _address(self, header_name):
        """Returns a list with the email addresses in the specified header."""
        def decode(text, encoding):
            """Decode a text. If an exception occurs when decoding returns the
            original text"""
            if encoding is None:
                return text
            try:
                return text.decode(encoding)
            except UnicodeDecodeError:
                return text

        def encode(text):
            """Encode a text to utf-8. If an exception occurs when encoding
            returns the original text"""
            try:
                return text.encode('utf-8')
            except UnicodeEncodeError:
                return text
        header_value = self.message[header_name]
        if not header_value:
            return []
        result = dict()
        header_value = header_value.replace('\n', ' ')
        pieces = email.header.decode_header(header_value)
        pieces = [decode(text, encoding) for text, encoding in pieces]
        header_value = u"".join(pieces).strip()
        name, address = email.utils.parseaddr(header_value)
        while address:
            result[address] = name or None
            index = header_value.find(address) + len(address)
            if index >= len(header_value):
                break
            if header_value[index] == '>':
                index += 1
            if index >= len(header_value):
                break
            if header_value[index] == ',':
                index += 1
            header_value = header_value[index:].strip()
            name, address = email.utils.parseaddr(header_value)
        self.names.update(result)
        addresses = [encode(address) for address in result.keys()]
        return sorted(addresses)

    def _address_str(self, header_name, join_str=', '):
        """
        Returns a string with the email addresses in the specified header
        concatenated by the value in the parameter `join_str`.

        Parameters
        ----------
        header_name: string
            Name of the header to parse.
        join_str: string
            String that will be used to concatenate the email addresses in
            the header.

        Returns
        -------
        addresses: string
            Email addresses in the header concatenated by the value in
            `join_str`.
        """
        return join_str.join(self._address(header_name))

    def _timestamp(self, header_name):
        """
        Returns the timestamp in the specified header.
        """
        header = self.message[header_name]
        if header is None:
            return None
        data = email.utils.parsedate_tz(header)
        if data is None:
            return None
        return email.utils.mktime_tz(data)

    def _timestamp_str(self, header_name):
        """
        Returns the timestamp in the specified header converted to string.
        """
        timestamp = self._timestamp(header_name)
        if timestamp is None:
            return ""
        return str(timestamp)

    def _date(self, header_name):
        """
        Returns the date of the specified header.
        """
        stamp = self._timestamp(header_name)
        if stamp is None or stamp == 'None':
            return None
        date = datetime.datetime.fromtimestamp(stamp)
        return date

    def _date_str(self, header_name):
        """
        Returns the date in the specified header converted to string.
        """
        date = self._date(header_name)
        if date is None:
            return ""
        return date.strftime('%Y-%m-%d %H:%M:%S')

    def _receivers(self):
        """
        Returns a set with the email addresses of the receivers of the message.
        """
        result = set()
        if self.to:
            result.update(set(self.to))
        if self.cc:
            result.update(set(self.cc))
        if self.bcc:
            result.update(set(self.bcc))
        received = self.message.get_all('Received')
        if received:
            headers = '\r\n'.join(received)
            new = set(self.re_recieved.findall(headers))
            result.update(new)
        return result
