#!/usr/bin/python3
# termrec

import bases
from utils.nolog import *; logstart('termrec')

npchars = '\1\2\3\4\5\6\16\17\20\21\22\23\24\25\26\27\30\31\34\35\36\37'
bases = bases.Bases()

@apcmd(metavar='<action>')
@aparg('output', type=argparse.FileType('wb'))
@aparg('command', nargs=argparse.REMAINDER)
def rec(cargs):
	def read(fd):
		nonlocal t
		s = os.read(fd, 1024)
		if (t is not None):
			tc = time.time()
			td = int((tc-t)*1000)
			if (td > 10): cargs.output.write(b'\0'+bases.toAlphabet(td, npchars).encode('ascii')+b'\0')
		cargs.output.write(s.replace(b'\0', b'\0\0'))
		t = time.time()
		return s

	t = None
	try: pty.spawn(cargs.command or os.getenv('SHELL', 'sh'), read)
	except KeyboardInterrupt as ex: exit(ex)

@apcmd(metavar='<action>')
@aparg('file', type=argparse.FileType('rb'))
@aparg('--noclear', action='store_true')
def play(cargs):
	fd = cargs.file.fileno()
	if (not cargs.noclear): clear()
	while (True):
		c = os.read(fd, 1)
		if (c == b'\0'):
			b = bytearray()
			while (True):
				c = os.read(fd, 1)
				if (not c or c == b'\0'): break
				b += c
			if (b): time.sleep(bases.fromAlphabet(b.decode('ascii'), npchars)/1000); continue
		if (not c): break
		sys.stdout.buffer.raw.write(c)

@apmain
def main(cargs):
	try: return cargs.func(cargs)
	except KeyboardInterrupt as ex: exit(ex)

if (__name__ == '__main__'): exit(main())
else: logimported()

# by Sdore, 2019
