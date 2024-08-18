import json.tool
import os
import gettext
import re
import time
import json
import csv
from math import *

from PySide6 import QtWidgets
from PySide6 import QtUiTools
from PySide6 import QtCore
from PySide6 import QtGui
from qt_material import apply_stylesheet

locales = {
    'en': QtCore.QLocale.Language.English,
    'ko': QtCore.QLocale.Language.Korean
}
langIndex = {'en': 0, 'ko': 1}
langList = ['en', 'ko']
themeIndex = {'Light': 0, 'Dark': 1}
themeList = ['Light', 'Dark']

t = gettext.translation('base', localedir='locale', languages=['en'])
t.install()
_ = t.gettext

app = QtWidgets.QApplication()
msgBox = QtWidgets.QMessageBox()

extra = {
    'font_family': 'Pretendard, Inter, "Segoe UI", "맑은 고딕"'
}

try:
    settingsFile = open('settings.json').read()
except FileNotFoundError:
    msgBox.setWindowTitle(('Error'))
    msgBox.setText(('The setting file is not found.'))
    msgBox.setIcon(msgBox.Icon.Critical)
    apply_stylesheet(msgBox, theme='light_blue.xml', extra=extra)
    msgBox.exec()
    quit()

try:
    settings = json.loads(settingsFile)
    if settings['lang'] not in langList:
        msgBox.setWindowTitle(('Error'))
        msgBox.setText(('The language setting is invalid.'))
        msgBox.setIcon(msgBox.Icon.Critical)
        apply_stylesheet(msgBox, theme='light_blue.xml', extra=extra)
        msgBox.exec()
        quit()
    elif settings['theme'] not in themeList:
        msgBox.setWindowTitle(('Error'))
        msgBox.setText(('The theme setting is invalid.'))
        msgBox.setIcon(msgBox.Icon.Critical)
        apply_stylesheet(msgBox, theme='light_blue.xml', extra=extra)
        msgBox.exec()
        quit() 
except KeyError:
    msgBox.setWindowTitle(('Error'))
    msgBox.setText(('The setting file is invalid.'))
    msgBox.setIcon(msgBox.Icon.Critical)
    apply_stylesheet(msgBox, theme='light_blue.xml', extra=extra)
    msgBox.exec()
    quit()

# print(memos)

# for m in memos:
#     print(m)

t = gettext.translation('base', localedir='locale', languages=[settings['lang']])
t.install()
_ = t.gettext

def loadUI(path: str):
    UIFile = path
    UIDir = os.path.dirname(__file__)
    UIPath = os.path.join(UIDir, UIFile)
    ret = QtUiTools.loadUiType(UIPath)

    if ret is None:
        quit()

    UIClass, QtBaseClass = ret
    
    return UIClass, QtBaseClass

UIClass, QtBaseClass = loadUI('OhCalendar.ui')          # Main window
UIClass2, QtBaseClass2 = loadUI('OhCalendarCalc.ui')    # Calc window
UIClass3, QtBaseClass3 = loadUI('OhCalendarSet.ui')     # Setting window

theme = settings['theme'].lower() + '_blue.xml'

class OhCalendar(UIClass, QtBaseClass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setLocale(locales[settings['lang']])

        # Translation
        self.btn1.setText(_('Calculator'))
        self.btn2.setText(_('Settings'))
        self.btn3.setText(_('Today'))
        self.btn4.setText(_('Bold'))

        # Clock
        self.clockUpdate()
        self.clock()

        # Theme
        apply_stylesheet(self, theme=theme, extra=extra)

        # Buttons
        self.calc = OhCalendarCalc()
        self.set = OhCalendarSet()
        self.btn1.clicked.connect(self.calc.show)
        self.btn2.clicked.connect(self.set.show)
        self.btn3.clicked.connect(self.today)
        self.calendar.selectionChanged.connect(self.importMemo)
        self.textEdit.textChanged.connect(self.saveMemo)
        self.btn4.clicked.connect(self.textBold)

        self.today()
        self.show()
    
    def clock(self):
        self.tm = QtCore.QTimer()
        self.tm.setInterval(500)
        self.tm.timeout.connect(self.clockUpdate)
        self.tm.start()

    def clockUpdate(self):
        currentTime = time.strftime('%H:%M')
        self.time.setText(_(currentTime))

    def today(self):
        a = QtCore.QDate.currentDate()      # a: (today)
        self.calendar.setSelectedDate(a)
        self.importMemo()

    def importMemo(self):       # BUG
        self.date = self.calendar.selectedDate().toString('yyyy-MM-dd')
        self.memo = ''
        try:
            with open('memos.csv', 'r') as f:
                memos = csv.reader(f, delimiter='|')
                for m in memos:
                    if m[0] == self.date:
                        self.memo = m[1]
                        break
                    else:
                        self.memo = ''
        except FileNotFoundError:
            msgBox.setWindowTitle(_('Error'))
            msgBox.setText(_('The memo file is not found. It will be created.'))
            msgBox.setIcon(msgBox.Icon.Critical)
            apply_stylesheet(msgBox, theme=theme, extra=extra)
            msgBox.exec()
            with open('memos.csv', 'x') as f:
                f.write('Date|Memo\n')
        except IndexError:
            msgBox.setWindowTitle(_('Error'))
            msgBox.setText(_('The memo file is invalid'))
            msgBox.setIcon(msgBox.Icon.Critical)
            apply_stylesheet(msgBox, theme=theme, extra=extra)
            msgBox.exec()
            quit()        
        # print(m)
        # i = 0
        # while memos[i][0] != self.date:
        #     i += 1
        # self.memo = memos[i][1]
        # print(self.date, self.memo)
        self.textEdit.setMarkdown(self.memo)
    
    def warning2(self):         # Invalid expression
        msgBox.setWindowTitle(_('Error'))
        msgBox.setText(_('The memo file is invalid.'))
        msgBox.setIcon(msgBox.Icon.Critical)
        apply_stylesheet(msgBox, theme=theme, extra=extra)
        msgBox.exec()

    def saveMemo(self):
        self.date = self.calendar.selectedDate().toString('yyyy-MM-dd')
        with open('memos.csv', 'r') as f1:
            memos = list(csv.reader(f1, delimiter='|'))
            for m in memos:
                if m[0] == self.date:
                    memos.remove(m)
            memos.append([self.date, self.textEdit.toMarkdown()])
            with open('memos.csv', 'w', newline='') as f2:
                wr = csv.writer(f2, delimiter='|')
                wr.writerows(memos)
    
    def textBold(self):
        fmt = QtGui.QTextCharFormat()
        weight = QtGui.QFont.Bold if self.checkFormat() else QtGui.QFont.Normal
        fmt.setFontWeight(weight)
        self.textStyle(fmt)
    
    def textStyle(self, format):
        cursor = self.textEdit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QtGui.QTextCursor.WordUnderCursor)
        cursor.mergeCharFormat(format)
        self.textEdit.mergeCurrentCharFormat(format)
        self.saveMemo()

    def checkFormat(self):
        if self.textEdit.textCursor().hasSelection():
            # print(self.textEdit.textCursor().selection().toHtml())
            if "**" in self.textEdit.textCursor().selection().toMarkdown():
                return False
            else:
                return True

        else:
            if self.textEdit.fontWeight() == QtGui.QFont.Bold:
                return True
            else:
                return False

class OhCalendarCalc(UIClass2, QtBaseClass2):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setLocale(locales[settings['lang']])

        # Translation, etc.
        self.result1.setText('')
        self.result2.setText('')
        self.input1.setPlaceholderText(_('Try "623+457"'))
        self.tabWidget.setTabText(0, _('Basic'))
        self.tabWidget.setTabText(1, _('Date'))
        self.input4.setSuffix(_('day(s)'))

        # Calculation
        self.input1.returnPressed.connect(self.calculate)
        self.input2.userDateChanged.connect(self.calculateDate)
        self.input3.currentTextChanged.connect(self.calculateDate)
        self.input4.valueChanged.connect(self.calculateDate)
        self.input2.setDate(QtCore.QDate(int(time.strftime('%Y')), int(time.strftime('%m')), int(time.strftime('%d'))))

        # Theme
        apply_stylesheet(self, theme=theme, extra=extra)

    def warning1(self):         # Invalid expression
        msgBox.setWindowTitle(_('Error'))
        msgBox.setText(_('Please enter a valid expression.'))
        msgBox.setIcon(msgBox.Icon.Warning)
        apply_stylesheet(msgBox, theme=theme, extra=extra)
        msgBox.exec()

    def calculate(self):
        expression = self.input1.text()
        if re.fullmatch(r'[0-9\+\-\*\/\.]+', expression) is None:       # "0123456789+-*/."
            self.warning1()
            return
        try:
            self.result = eval(expression)
            self.result1.setText('=' + str(round(self.result, 10)))
        except SyntaxError:
            self.warning1()
            return
        
    def calculateDate(self):
        startDate = self.input2.date()
        operation = self.input3.currentText()
        days = self.input4.value()
        if operation == '+':
            result = startDate.addDays(days)
        else:
            result = startDate.addDays(0-days)
        self.result2.setText('=' + result.toString('yyyy-MM-dd'))

class OhCalendarSet(UIClass3, QtBaseClass3):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setLocale(locales[settings['lang']])

        self.groupBox1.setTitle(_('Information'))
        self.groupBox2.setTitle(_('Language'))
        self.groupBox3.setTitle(_('Theme'))
        self.label1.setText('OhCalendar V1.0')
        self.label2.setText(_('Please restart OhCalendar after you change settings.'))
        self.langSelect.setItemText(0, _('English'))
        self.langSelect.setItemText(1, _('Korean'))
        self.langSelect.currentIndexChanged.connect(self.changeLang)
        self.themeSelect.setItemText(0, _('Light'))
        self.themeSelect.setItemText(1, _('Dark'))
        self.themeSelect.currentIndexChanged.connect(self.changeTheme)

        self.langSelect.setCurrentIndex(langIndex[settings['lang']])
        self.themeSelect.setCurrentIndex(themeIndex[settings['theme']])

        apply_stylesheet(self, theme=theme, extra=extra)

    def changeLang(self):
        settings['lang'] = langList[self.langSelect.currentIndex()]
        file = open('settings.json', 'w')
        file.write(json.dumps(settings))
        file.close()

    def changeTheme(self):
        settings['theme'] = themeList[self.themeSelect.currentIndex()]
        file = open('settings.json', 'w')
        file.write(json.dumps(settings))
        file.close()

win = OhCalendar()
app.exec()