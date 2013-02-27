import sys
import subprocess
import tempfile

import progressbar


def bold(text):
    """ Return bolded text.
    """
    return u'\x1b[1m%s\x1b[22m' % text


def highlight_white(text):
    """ Return text highlighted in white.
    """
    return u'\x1b[1;37;7m%s\x1b[22;27;39m' % text


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
        text = sep.join(unicode(x) for x in args).format(**kwargs) + end
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
        for i, (choice, text) in enumerate(choices):
            self.p(u'[{indice}] {text}', indice=i + 1, text=text)
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
        if self._editor is None:
            printer.p('Warning: no editor found, skipping edit')
            return text
        with tempfile.NamedTemporaryFile(mode='w+', suffix='kolekto-edit') as ftmp:
            ftmp.write(text.encode('utf-8'))
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
