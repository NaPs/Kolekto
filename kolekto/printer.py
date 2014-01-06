import sys
import subprocess
import tempfile

import progressbar
from lxml import etree


COLORS = {'black': (30, 40),
          'red': (31, 41),
          'green': (32, 42),
          'yellow': (33, 43),
          'blue': (34, 44),
          'magenta': (35, 45),
          'cyan': (36, 46),
          'light_gray': (37, 47),
          'dark_gray': (90, 100),
          'light_red': (91, 101),
          'light_green': (92, 102),
          'light_yellow': (93, 103),
          'light_blue': (94, 104),
          'light_magenta': (95, 105),
          'light_cyan': (96, 106),
          'white': (97, 107)}


class ConsoleFormatter(object):

    """ Convert an XML markup to VT100 control codes.
    """

    def __init__(self, root_elem):
        self.text = ''
        self._last_color_fg = 39  # Default color
        self._last_color_bg = 49  # Default background
        self._parse(root_elem)

    @classmethod
    def from_text(cls, text):
        return cls(etree.fromstring('<root>%s</root>' % text))

    def append(self, text):
        self.text += text

    def _parse(self, elem):
        if elem.text is not None:
            self.append(elem.text)

        for child in elem:
            func = getattr(self, 'tag_' + child.tag)
            func(child)
            if child.tail is not None:
                self.text += child.tail

    #
    # Tags definition
    #

    def tag_color(self, elem):
        fg = COLORS.get(elem.get('fg'), [None, None])[0]
        bg = COLORS.get(elem.get('bg'), [None, None])[1]
        last_fg = self._last_color_fg
        last_bg = self._last_color_bg
        if fg is not None:
            self._last_color_fg = fg
            self.append('\x1b[%dm' % fg)
        if bg is not None:
            self._last_color_bg = bg
            self.append('\x1b[%dm' % bg)
        self._parse(elem)
        if fg is not None:
            self.append('\x1b[%dm' % last_fg)
        if bg is not None:
            self.append('\x1b[%dm' % last_bg)

    def tag_b(self, elem):
        self.append('\x1b[1m')
        self._parse(elem)
        self.append('\x1b[21m')

    def tag_inv(self, elem):
        self.append('\x1b[37;7m')
        self._parse(elem)
        self.append('\x1b[27;39m')

    def tag_dim(self, elem):
        self.append('\x1b[2m')
        self._parse(elem)
        self.append('\x1b[22m')

    def tag_u(self, elem):
        self.append('\x1b[4m')
        self._parse(elem)
        self.append('\x1b[24m')


class ProgressContext(object):

    """ A context for progress bar allowing to use the with statement.
    """

    def __init__(self, *args, **kwargs):
        self.pbar = progressbar.ProgressBar(*args, **kwargs)
        self.count = 0

    def __call__(self, value):
        self.count += value
        self.pbar.update(self.count)

    def __enter__(self):
        self.pbar.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pbar.finish()


def option(option, text, **kwargs):
    """ Simple shortcut to construct an option for the KolektoPrinter.choices method.
    """
    return option, text, kwargs


class KolektoPrinter(object):

    """ Handle print and user interactions.
    """

    PROGRESS_WIDGETS = (' ', progressbar.Percentage(), ' ',
                        progressbar.Bar(left='[', right=']', marker='='), ' ',
                        progressbar.FileTransferSpeed(), ' | ',
                        progressbar.ETA())
    PROGESS_TASK_WIDGETS = (' ', progressbar.Percentage(), ' ',
                            progressbar.Bar(left='[', right=']', marker='='), ' ',
                            progressbar.SimpleProgress(), ' | ',
                            progressbar.ETA())

    def __init__(self, output=sys.stdout, err=sys.stderr, verbose=False, debug=False, encoding='utf8', editor=None):
        self._output = output
        self._err = err
        self._verbose = verbose
        self._debug = debug
        self._encoding = encoding
        self._editor = editor

    @property
    def output(self):
        return self._output

    def _print(self, *args, **kwargs):
        sep = kwargs.pop('sep', u' ')
        end = kwargs.pop('end', u'\n')
        err = kwargs.pop('err', False)
        markup = kwargs.pop('markup', True)
        kwargs = dict((k, u'<![CDATA[%s]]>' % v) for k, v in kwargs.iteritems())
        text = sep.join(unicode(x) for x in args).format(**kwargs) + end
        if markup:
            text = ConsoleFormatter.from_text(text).text
        if err:
            self._err.write(text.encode(self._encoding))
        else:
            self._output.write(text.encode(self._encoding))

    def configure(self, output=None, verbose=None, debug=None, encoding=None, editor=None):
        if output is not None:
            self._output = output
        if verbose is not None:
            self._verbose = verbose
        if debug is not None:
            self._debug = debug
        if encoding is not None:
            self._encoding = encoding
        if editor is not None:
            self._editor = editor

    def debug(self, *args, **kwargs):
        if self._debug:
            args = ('[debug]',) + args
            self._print(*args, err=True, **kwargs)

    def verbose(self, *args, **kwargs):
        if self._verbose or self._debug:
            self._print(*args, **kwargs)

    def p(self, *args, **kwargs):
        self._print(*args, **kwargs)

    def choice(self, choices):
        for i, (option, text, args) in enumerate(choices):
            self.p(u'[{indice}] ' + text, indice=i + 1, **args)
        self.p('')
        while True:
            chosen = raw_input('Choice [1-{0}]? '.format(len(choices)))
            if chosen.isdigit() and 1 <= int(chosen) <= len(choices):
                return choices[int(chosen) - 1][0]

    def input(self, prompt, default=None):
        if default is None:
            default_text = u''
        else:
            default_text = u' [{0}]'.format(default)
        prompt = u'{0}{1}? '.format(prompt, default_text)
        answer = raw_input(prompt.encode(self._encoding)).rstrip('\n').decode(self._encoding)
        if not answer:
            answer = default
        return answer

    def ask(self, question, default=False):
        """ Ask a y/n question to the user.
        """
        choices = '[%s/%s]' % ('Y' if default else 'y', 'n' if default else 'N')
        while True:
            response = raw_input('%s %s' % (question, choices)).strip()
            if not response:
                return default
            elif response in 'yYoO':
                return True
            elif response in 'nN':
                return False

    def edit(self, text):
        """ Edit a text using an external editor.
        """
        if isinstance(text, unicode):
            text = text.encode(self._encoding)
        if self._editor is None:
            printer.p('Warning: no editor found, skipping edit')
            return text
        with tempfile.NamedTemporaryFile(mode='w+', suffix='kolekto-edit') as ftmp:
            ftmp.write(text)
            ftmp.flush()
            subprocess.Popen([self._editor, ftmp.name]).wait()
            ftmp.seek(0)
            edited = ftmp.read()
            return edited

    def progress(self, max, task=False):
        if task:
            return ProgressContext(widgets=self.PROGESS_TASK_WIDGETS, maxval=max)
        else:
            return ProgressContext(widgets=self.PROGRESS_WIDGETS, maxval=max)

# Instanciate the default printer:
printer = KolektoPrinter()
