from learnbot_dsl.learnbotCode.CodeEdit import *
from learnbot_dsl.learnbotCode.Highlighter import *
from enum import Enum, auto
from PySide2 import QtWidgets

class Severity(Enum):
    WARNING = auto()
    ERROR = auto()

class Notification(QtWidgets.QWidget):
    resized = QtCore.Signal()

    def __init__(self, src, start, end = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.src = src

        self.vLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.vLayout)

        self.summaryLayout = QtWidgets.QHBoxLayout()
        self.vLayout.addLayout(self.summaryLayout)

        self.icon = QtWidgets.QLabel()
        self.icon.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Ignored)
        self.summaryLayout.addWidget(self.icon)

        self.message = QtWidgets.QLabel()
        self.message.setWordWrap(True)
        font = self.message.font()
        font.setBold(True)
        self.message.setFont(font)
        self.summaryLayout.addWidget(self.message)

        self.position = QtWidgets.QLabel()
        font = self.position.font()
        font.setItalic(True)
        self.position.setFont(font)
        self.vLayout.addWidget(self.position)

        self.snippet = CodeEdit()
        self.snippet.setReadOnly(True)
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        self.snippet.setFont(font)
        self.snippet.setReadOnly(True)
        self.snippet.setOffset(start[1]-1)
        self.vLayout.addWidget(self.snippet)

        self.hints = QtWidgets.QVBoxLayout()
        self.vLayout.addLayout(self.hints)

        self.highlighter = Highlighter(self.snippet.document())
        self.setPosition(start, end)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitSnippetToContent()

    def fitSnippetToContent(self):
        margins = self.snippet.contentsMargins()
        height = self.snippet.document().documentMargin() * 2 \
                + margins.top() \
                + margins.bottom()

        for line in range(self.snippet.blockCount()):
            block = self.snippet.document().findBlock(line)
            height += self.snippet.blockBoundingRect(block).height()

        if self.snippet.horizontalScrollBar().isVisible():
            height += self.snippet.horizontalScrollBar().height()

        self.snippet.setFixedHeight(height)
        self.resized.emit()

    def setSeverity(self, severity):
        if severity == Severity.ERROR:
            icon = QtGui.QIcon.fromTheme('dialog-error')
        elif severity == Severity.WARNING:
            icon = QtGui.QIcon.fromTheme('dialog-warning')

        self.icon.setPixmap(icon.pixmap(QtCore.QSize(16, 16)))

    def setMessage(self, message):
        self.message.setText(message)

    def setPosition(self, start, end = None):
        self.start = start
        self.end = end

        if end:
            params = (start[0], start[1], end[0], end[1])
            lines = end[0] - start[0] + 1
            position = self.tr('at %s:%s—%s:%s') % params
            snippet = '\n'.join(self.src.split('\n')[start[0]-1:end[0]])
        else:
            params = (start[0], start[1])
            lines = 1
            position = self.tr('at %s:%s') % params
            snippet = self.src.split('\n')[start[0]-1]

        self.position.setText(position)
        self.snippet.setPlainText(snippet)

    def setHints(self, hints):
        for _ in range(self.hints.count()):
            self.vLayout.itemAt().widget().setParent(None)

        for hint in hints:
               item = QtWidgets.QLabel(self)
               item.setText(self.tr('<b>Hint:</b> ') + hint)
               self.hints.addWidget(item)

class ParseError(Notification):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO
        hints = [
            self.tr('did you forget something while typing the <code>%s</code>?') % 'TODO',
        ]

        self.setSeverity(Severity.ERROR)
        self.setMessage(self.tr('Parse error'))
        self.setHints(hints)

class TypeMismatch(Notification):
    def __init__(self, expected, got, *args, **kwargs):
        super().__init__(*args, **kwargs)

        hints = [
            self.tr('check the marked expression: does it really return a value of type <code>%s</code>?') % expected,
            self.tr('did you make a typo while writing the expression? Check the operators!'),
            self.tr('be careful with operator precedence!'),
        ]

        self.setSeverity(Severity.WARNING)
        self.setMessage(self.tr('Type mismatch: expected %s, got %s') % (expected, got))
        self.setHints(hints)