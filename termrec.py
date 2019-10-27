#!/usr/bin/python3
# termrec

import bases
from utils.nolog import *; logstart('termrec')

npchars = '\1\2\3\4\5\6\16\17\20\21\22\23\24\25\26\27\30\31\34\35\36\37'
bases = bases.Bases()

@apcmd(metavar='<action>')
@aparg('output', help="Output file", type=argparse.FileType('wb'))
@aparg('command', help="Override command to run ($SHELL or /bin/sh by default)", nargs=argparse.REMAINDER)
@aparg('-s', '--speed', metavar='speed', help="Playback speed", default=1, type=float)
@aparg('-i', '--maxidle', metavar='maxidle', help="Maximum idle time", default=inf, type=float)
def rec(cargs):
	""" Record a terminal session. """

	if (os.getenv('TERMREC')): exit("You are trying to start a recording inside an existing record session! If this is what you want, unset TERMREC environment variable.")

	ofd = cargs.output.fileno()
	speed, maxidle = 1/cargs.speed, cargs.maxidle

	def read(fd):
		nonlocal t
		s = os.read(fd, 1024)
		if (t is not None):
			tc = time.time()
			td = int(min(tc-t, maxidle)*speed*1000)
			if (td > 10): os.write(ofd, b'\0'+bases.toAlphabet(td, npchars).encode('ascii')+b'\0')
		os.write(ofd, s.replace(b'\0', b'\0\0'))
		t = time.time()
		return s

	t = None
	os.environ['TERMREC'] = '1'
	try: pty.spawn(cargs.command or os.getenv('SHELL', '/bin/sh'), read)
	finally: cargs.output.close()

@apcmd(metavar='<action>')
@aparg('file', help="Recording file", type=argparse.FileType('rb'))
@aparg('-s', '--speed', metavar='speed', help="Playback speed", default=1, type=float)
@aparg('-i', '--maxidle', metavar='maxidle', help="Maximum idle time", default=inf, type=float)
@aparg('--noclear', help="Do not clear terminal", action='store_true')
def play(cargs):
	""" Play recorded terminal session. """

	if (os.getenv('TERMREC')): exit("You are trying to play a recording inside an record session! If this is what you want, unset TERMREC environment variable.")

	if (not cargs.noclear): clear()

	fd = cargs.file.fileno()
	speed, maxidle = 1/cargs.speed, cargs.maxidle

	while (True):
		c = os.read(fd, 1)
		if (c == b'\0'):
			b = bytearray()
			while (True):
				c = os.read(fd, 1)
				if (not c or c == b'\0'): break
				b += c
			if (b): time.sleep(min(bases.fromAlphabet(b.decode('ascii'), npchars)*speed/1000, maxidle)); continue
		if (not c): break
		sys.stdout.buffer.raw.write(c)

@apcmd(metavar='<action>')
@aparg('infile', help="Recording file", type=argparse.FileType('rb'))
@aparg('outfile', help="Output file", type=argparse.FileType('wb'))
@aparg('-s', '--speed', metavar='speed', help="Playback speed", default=1, type=float)
@aparg('-i', '--maxidle', metavar='maxidle', help="Maximum idle time", default=inf, type=float)
def rewrite(cargs):
	""" Rewrite recording with applying specified parameters as if it was recorded with them. """
	ifd, ofd = cargs.infile.fileno(), cargs.outfile.fileno()
	speed, maxidle = 1/cargs.speed, cargs.maxidle

	try:
		while (True):
			c = os.read(ifd, 1)
			if (c == b'\0'):
				b = bytearray()
				while (True):
					c = os.read(ifd, 1)
					if (not c or c == b'\0'): break
					b += c
				if (b): os.write(ofd, b'\0'+bases.toAlphabet(int(min(bases.fromAlphabet(b.decode('ascii'), npchars)*speed/1000, maxidle)*1000), npchars).encode('ascii')+b'\0')
				else: os.write(ofd, b'\0\0')
				continue
			if (not c): break
			os.write(ofd, c)
	finally: cargs.outfile.close()


@apmain
def main(cargs):
	try: return cargs.func(cargs)
	except KeyboardInterrupt as ex: exit(ex)

if (__name__ == '__main__'): exit(main())
else: logimported()

# by Sdore, 2019
