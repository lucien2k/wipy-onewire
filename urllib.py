"""Open an arbitrary URL.

Adapted for Micropython by Alex Cowan <acowan@gmail.com>

Includes some elements from the original urllib and urlencode libraries for Python
"""

import socket
try:
    import ussl as ssl
except:
    import ssl

class URLOpener:
    def __init__(self, url, post_data={}):
        self.code = 0
        self.headers = {}
        self.body = ""
        self.url = url
        [scheme, host, path, data] = urlparse(self.url)
        if scheme == 'http':
            addr = socket.getaddrinfo(host, 80)[0][-1]
            s = socket.socket()
            s.settimeout(5)
            s.connect(addr)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            s = ssl.wrap_socket(sock)
            s.connect(socket.getaddrinfo(host, 443)[0][4])
        if post_data:
            data = urlencode(post_data)
            #print('POST %s HTTP/1.0\r\nHost: %s\r\n\r\n%s\r\n' % (path or '/', host, data.strip()))
            s.send(b'POST %s HTTP/1.0\r\nHost: %s\r\n\r\n%s\r\n' % (path or '/', host, data.strip()))
        else:
            #print('GET %s%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path or '/', '?'+data.strip(), host))
            s.send(b'GET %s%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path or '/', '?'+data.strip(), host))
        self.raw = ""
        while 1:
            recv = s.recv(1024)
            if len(recv) == 0: break
            self.raw += recv.decode()
        s.close()
        self._parse_result()

    def read(self):
        return self.body

    def _parse_result(self):
    	header = 1
    	for line in self.raw.split('\r\n'):
            line = line.strip()
            if line == '':
                 header = 0
            if header and line[0:4] == 'HTTP':
                data = line.split(' ')
                self.code = int(data[1])
                continue
            if header and len(line.split(':')) >= 2:
                data = line.split(':')
                self.headers[data[0]] = ':'.join(data[1:])
                continue
            if not header:
                self.body += line
    	return

def urlparse(url):
    scheme = url.split('://')[0]
    url = url.split('://')[1]
    host = url.split('/')[0]
    path = '/'
    data = ""
    if host != url:
        path = ''.join(url.split('/')[1:])
        if path.count('?'):
            if path.count('?') > 1:
                raise Exception('URL malformed, too many ?')
            [path, data] = path.split('?')
    return [scheme, host, path, data]

def urlopen(url, post_data={}):
    orig_url = url
    attempts = 0
    result = URLOpener(url, post_data)
    ## Maximum of 4 redirects
    while attempts < 4:
        attempts += 1
        if result.code in (301, 302):
            url = result.headers.get('Location', '')
            if not url.count('://'):
                [scheme, host, path, data] = urlparse(orig_url)
                url = '%s://%s%s' % (scheme, host, url)
            if url:
                result = URLOpener(url)
            else:
                raise Exception('URL returned a redirect but one was not found')
        else:
            return result
    return result

_hextochr = {'5E': '^', '5D': ']', '5F': '_', '5A': 'Z', '5C': '\\', '5B': '[', '24': '$', '25': '%', '26': '&', '27': "'", '20': ' ', '21': '!', '22': '"', '23': '#', '28': '(', '29': ')', '5e': '^', '5d': ']', '5f': '_', '5a': 'Z', '5c': '\\', '5b': '[', '6A': 'j', '6B': 'k', '2D': '-', '2E': '.', '2F': '/', '6C': 'l', '2A': '*', '2B': '+', '2C': ',', '6D': 'm', '6E': 'n', '60': '`', '59': 'Y', '6F': 'o', '55': 'U', '54': 'T', '57': 'W', '56': 'V', '51': 'Q', '62': 'b', '53': 'S', '52': 'R', '2d': '-', '2e': '.', '2f': '/', '63': 'c', '2a': '*', '2b': '+', '2c': ',', '64': 'd', '65': 'e', '67': 'g', '50': 'P', '3C': '<', '3B': ';', '3A': ':', '3F': '?', '3E': '>', '3D': '=', '02': '\x02', '03': '\x03', '00': '\x00', '01': '\x01', '06': '\x06', '07': '\x07', '04': '\x04', '05': '\x05', '08': '\x08', '09': '\t', '3c': '<', '3b': ';', '3a': ':', '3f': '?', '3e': '>', '3d': '=', '0B': '\x0b', '0C': '\x0c', '0A': '\n', '0F': '\x0f', '0D': '\r', '0E': '\x0e', '39': '9', '38': '8', '33': '3', '32': '2', '31': '1', '30': '0', '37': '7', '36': '6', '35': '5', '34': '4', '0b': '\x0b', '0c': '\x0c', '0a': '\n', '0f': '\x0f', '0d': '\r', '0e': '\x0e', '58': 'X', '1A': '\x1a', '61': 'a', '1C': '\x1c', '1B': '\x1b', '1E': '\x1e', '1D': '\x1d', '66': 'f', '1F': '\x1f', '68': 'h', '69': 'i', '1a': '\x1a', '1c': '\x1c', '1b': '\x1b', '1e': '\x1e', '1d': '\x1d', '1f': '\x1f', '4A': 'J', '6a': 'j', '6b': 'k', '6c': 'l', '6d': 'm', '6e': 'n', '6f': 'o', '11': '\x11', '10': '\x10', '13': '\x13', '12': '\x12', '15': '\x15', '14': '\x14', '17': '\x17', '16': '\x16', '19': '\x19', '18': '\x18', '7f': '\x7f', '7e': '~', '7d': '}', '7c': '|', '7b': '{', '7a': 'z', '7F': '\x7f', '7E': '~', '7D': '}', '7C': '|', '7B': '{', '7A': 'z', '49': 'I', '46': 'F', '47': 'G', '44': 'D', '45': 'E', '42': 'B', '43': 'C', '40': '@', '41': 'A', '77': 'w', '76': 'v', '75': 'u', '74': 't', '73': 's', '72': 'r', '71': 'q', '70': 'p', '4F': 'O', '4D': 'M', '4E': 'N', '4B': 'K', '4C': 'L', '79': 'y', '78': 'x', '48': 'H', '4f': 'O', '4d': 'M', '4e': 'N', '4b': 'K', '4c': 'L', '4a': 'J'}

def unquote(s):
    """unquote('abc%20def') -> 'abc def'."""
    res = s.split('%')
    for i in xrange(1, len(res)):
        item = res[i]
        try:
            res[i] = _hextochr[item[:2]] + item[2:]
        except KeyError:
            res[i] = '%' + item
    return "".join(res)

def unquote_plus(s):
    """unquote('%7e/abc+def') -> '~/abc def'"""
    s = s.replace('+', ' ')
    return unquote(s)

always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789' '_.-')
_safemaps = {}

def quote(s, safe = '/'):
    cachekey = (safe, always_safe)
    try:
        safe_map = _safemaps[cachekey]
    except KeyError:
        safe += always_safe
        safe_map = {}
        for i in range(256):
            c = chr(i)
            safe_map[c] = (c in safe) and c or ('%%%02X' % i)
        _safemaps[cachekey] = safe_map
    res = map(safe_map.__getitem__, s)
    return ''.join(res)

def quote_plus(s, safe = ''):
    if ' ' in s:
        s = quote(s, safe + ' ')
        return s.replace(' ', '+')
    return quote(s, safe)

def urlencode(query):
    if isinstance(query, dict):
        query = query.items()
    l = []
    for k, v in query:
        k = quote_plus(str(k))
        v = quote_plus(str(v))
        l.append(k + '=' + v)
    return '&'.join(l)


