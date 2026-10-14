import os
import shutil
import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
                             QFrame, QGroupBox, QLineEdit, QApplication)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QPixmap
from .translation import Translator
from . import paths, links

logger = logging.getLogger(__name__)


class AboutTab(QWidget):
    def __init__(self, translator: Translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.initUI()
        self.translator.language_changed.connect(self.update_translations)

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        top = QHBoxLayout()
        top.setSpacing(20)

        logo_box = QVBoxLayout()
        logo_box.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.logo = QLabel()
        logo_path = paths.resource_path('assets', 'icon.png')
        if os.path.exists(logo_path):
            pm = QPixmap(logo_path)
            if not pm.isNull():
                self.logo.setPixmap(
                    pm.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_box.addWidget(self.logo)

        info_box = QVBoxLayout()
        info_box.setSpacing(6)

        self.lbl_title = QLabel(self.translator.translate('app_title'))
        self.lbl_title.setObjectName('AboutTitleLabel')
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.lbl_version = QLabel(self.translator.translate('version'))
        self.lbl_version.setObjectName('AboutVersionLabel')
        self.lbl_version.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.lbl_author = QLabel(self.translator.translate('author'))
        self.lbl_author.setObjectName('AboutAuthorLabel')
        self.lbl_author.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.lbl_desc = QLabel(self.translator.translate('description'))
        self.lbl_desc.setObjectName('AboutDescriptionLabel')
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setAlignment(Qt.AlignmentFlag.AlignLeft)

        info_box.addWidget(self.lbl_title)
        info_box.addWidget(self.lbl_version)
        info_box.addWidget(self.lbl_author)
        info_box.addSpacing(8)
        info_box.addWidget(self.lbl_desc)

        top.addLayout(logo_box, 0)
        top.addLayout(info_box, 1)
        layout.addLayout(top)

        line = QFrame(self)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(16)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_github = QPushButton(self.translator.translate('github'))
        self.btn_github.setObjectName('AboutButton')
        self.btn_github.clicked.connect(self.on_github_clicked)

        self.btn_issues = QPushButton(self.translator.translate('issues'))
        self.btn_issues.setObjectName('AboutButton')
        self.btn_issues.clicked.connect(self.on_issues_clicked)

        self.btn_docs = QPushButton(self.translator.translate('docs'))
        self.btn_docs.setObjectName('AboutButton')
        self.btn_docs.clicked.connect(self.on_docs_clicked)

        buttons_layout.addWidget(self.btn_github)
        buttons_layout.addWidget(self.btn_issues)
        buttons_layout.addWidget(self.btn_docs)

        layout.addLayout(buttons_layout)

        # Deno support section
        self.deno_group = QGroupBox(self.translator.translate('deno_title'))
        deno_layout = QVBoxLayout(self.deno_group)

        self.deno_text = QLabel(self.translator.translate('deno_text'))
        self.deno_text.setWordWrap(True)
        self.deno_text.setObjectName('HintLabel')
        deno_layout.addWidget(self.deno_text)

        command_row = QHBoxLayout()
        self.deno_command = QLineEdit('irm https://deno.land/install.ps1 | iex')
        self.deno_command.setReadOnly(True)
        command_row.addWidget(self.deno_command, 1)

        self.btn_copy_deno = QPushButton(self.translator.translate('copy_command'))
        self.btn_copy_deno.setObjectName('SecondaryButton')
        self.btn_copy_deno.clicked.connect(self.on_copy_deno)
        command_row.addWidget(self.btn_copy_deno)
        deno_layout.addLayout(command_row)

        self.deno_status = QLabel()
        self.deno_status.setObjectName('HintLabel')
        deno_layout.addWidget(self.deno_status)
        self.refresh_deno_status()

        layout.addWidget(self.deno_group)
        layout.addStretch(1)

    def refresh_deno_status(self):
        if shutil.which('deno'):
            self.deno_status.setText(self.translator.translate('deno_found'))
        else:
            self.deno_status.setText(self.translator.translate('deno_missing'))

    def on_copy_deno(self):
        QApplication.clipboard().setText(self.deno_command.text())
        self.deno_status.setText(self.translator.translate('command_copied'))

    def update_translations(self):
        self.lbl_title.setText(self.translator.translate('app_title'))
        self.lbl_version.setText(self.translator.translate('version'))
        self.lbl_author.setText(self.translator.translate('author'))
        self.lbl_desc.setText(self.translator.translate('description'))
        self.btn_github.setText(self.translator.translate('github'))
        self.btn_issues.setText(self.translator.translate('issues'))
        self.btn_docs.setText(self.translator.translate('docs'))
        self.deno_group.setTitle(self.translator.translate('deno_title'))
        self.deno_text.setText(self.translator.translate('deno_text'))
        self.btn_copy_deno.setText(self.translator.translate('copy_command'))
        self.refresh_deno_status()

    def on_github_clicked(self):
        QDesktopServices.openUrl(QUrl(links.GITHUB))

    def on_issues_clicked(self):
        QDesktopServices.openUrl(QUrl(links.ISSUES))

    def on_docs_clicked(self):
        QDesktopServices.openUrl(QUrl(links.DOCS))
