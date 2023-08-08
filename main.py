import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QLineEdit, QToolBar, QVBoxLayout, QWidget, QTabWidget, QPushButton, QHBoxLayout, QLabel, QDialog, QVBoxLayout, QDialogButtonBox, QComboBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, pyqtSignal, QSettings, Qt
from PyQt5.QtGui import QIcon, QPalette, QColor

class BrowserTab(QWebEngineView):
    urlChangedSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.urlChanged.connect(self.update_url)

    def update_url(self, q):
        self.urlChangedSignal.emit(q.toString())

    def set_custom_content(self):
        custom_content = """
        <html>
            <head>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 10px;
                        background-color: #f4f4f4;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        height: 100%;
                    }
                    h1 {
                        color: #333;
                        margin-bottom: 20px;
                    }
                    .button-container {
                        margin-top: 20px;
                    }
                </style>
            </head>
            <body>
                <h1>Welcome to Browser X!</h1>
                <div class="button-container">
                    <button onclick="window.location.href='https://duckduckgo.com'">Go to DuckDuckGo</button>
                </div>
            </body>
        </html>
        """
        self.setHtml(custom_content, QUrl("about:blank"))

class BrowserX(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Browser X")
        self.resize(1024, 768)  # Set an initial window size

        self.settings = QSettings("BrowserX", "Settings")
        self.homepage_url = self.settings.value("homepage_url", "https://duckduckgo.com")
        self.dark_mode = self.settings.value("dark_mode", False)

        self.browser_tabs = QTabWidget()
        self.browser_tabs.setTabsClosable(True)
        self.browser_tabs.tabCloseRequested.connect(self.close_tab)

        self.new_tab_button = QPushButton()
        self.new_tab_button.setIcon(QIcon("images/plus.png"))
        self.new_tab_button.setIconSize(self.new_tab_button.sizeHint())  # Set a fixed size for the icon
        self.new_tab_button.clicked.connect(self.add_new_tab)

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        back_action = QAction(QIcon("images/back.png"), "Back", self)
        back_action.triggered.connect(self.go_back)
        self.toolbar.addAction(back_action)

        forward_action = QAction(QIcon("images/forward.png"), "Forward", self)
        forward_action.triggered.connect(self.go_forward)
        self.toolbar.addAction(forward_action)

        reload_action = QAction(QIcon("images/reload.png"), "Reload", self)
        reload_action.triggered.connect(self.reload_page)
        self.toolbar.addAction(reload_action)

        home_action = QAction(QIcon("images/home.png"), "Home", self)
        home_action.triggered.connect(self.navigate_home)
        self.toolbar.addAction(home_action)

        settings_action = QAction(QIcon("images/settings.png"), "Settings", self)
        settings_action.triggered.connect(self.show_settings)
        self.toolbar.addAction(settings_action)

        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.load_page)
        self.search_bar.setPlaceholderText("Enter search terms or website URL")
        self.toolbar.addWidget(self.search_bar)

        self.toolbar.addWidget(self.new_tab_button)

        self.browser_tabs.currentChanged.connect(self.tab_changed)

        layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(layout)
        layout.addWidget(self.toolbar)

        nav_bar_layout = QHBoxLayout()
        nav_bar_layout.setContentsMargins(10, 0, 10, 0)
        nav_label = QLabel("URL: ")
        self.url_label = QLabel(self.homepage_url)
        nav_bar_layout.addWidget(nav_label)
        nav_bar_layout.addWidget(self.url_label)
        layout.addLayout(nav_bar_layout)

        layout.addWidget(self.browser_tabs)
        self.setCentralWidget(container)

        self.update_theme()

    def update_theme(self):
        if self.dark_mode:
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            self.setPalette(palette)
        else:
            self.setPalette(QApplication.palette())

    def set_homepage(self, url):
        self.homepage_url = url
        self.url_label.setText(url)
        self.settings.setValue("homepage_url", url)

    def load_page(self):
        query = self.search_bar.text()
        if not query:
            return

        current_tab = self.browser_tabs.currentWidget()
        if not current_tab:
            current_tab = self.add_new_tab()

        if query.startswith('http') or query.startswith('https'):
            if not query.startswith('https'):
                query = 'https://' + query
            current_tab.setUrl(QUrl(query))
        else:
            search_url = 'https://duckduckgo.com/?q=' + query.replace(' ', '+')
            current_tab.setUrl(QUrl(search_url))

    def update_url(self, q):
        self.url_label.setText(q)
        self.search_bar.setText(q)

    def tab_changed(self, index):
        current_tab = self.browser_tabs.widget(index)
        if current_tab:
            current_tab.urlChangedSignal.connect(self.update_url)

    def go_back(self):
        current_tab = self.browser_tabs.currentWidget()
        if current_tab:
            current_tab.back()

    def go_forward(self):
        current_tab = self.browser_tabs.currentWidget()
        if current_tab:
            current_tab.forward()

    def reload_page(self):
        current_tab = self.browser_tabs.currentWidget()
        if current_tab:
            current_tab.reload()

    def navigate_home(self):
        current_tab = self.browser_tabs.currentWidget()
        if current_tab:
            current_tab.setUrl(QUrl(self.homepage_url))

    def add_new_tab(self):
        new_tab = BrowserTab()
        new_tab.urlChangedSignal.connect(self.update_url)
        new_tab.set_custom_content()  # Set custom content for about:blank

        tab_index = self.browser_tabs.addTab(new_tab, "New Tab")  # Set the title for the new tab
        self.browser_tabs.setCurrentIndex(tab_index)
        return new_tab

    def close_tab(self, index):
        tab_to_remove = self.browser_tabs.widget(index)
        if tab_to_remove:
            tab_to_remove.deleteLater()
            self.browser_tabs.removeTab(index)

    def show_settings(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec_()

class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Settings")

        self.layout = QVBoxLayout()

        self.homepage_label = QLabel("Homepage:")
        self.homepage_edit = QLineEdit()
        self.homepage_edit.setText(parent.homepage_url)
        self.layout.addWidget(self.homepage_label)
        self.layout.addWidget(self.homepage_edit)

        self.theme_label = QLabel("Theme:")
        self.theme_combobox = QComboBox()
        self.theme_combobox.addItem("Light")
        self.theme_combobox.addItem("Dark")
        if parent.dark_mode:
            self.theme_combobox.setCurrentIndex(1)
        self.layout.addWidget(self.theme_label)
        self.layout.addWidget(self.theme_combobox)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.save_settings)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def save_settings(self):
        homepage_url = self.homepage_edit.text()
        self.parent().set_homepage(homepage_url)

        dark_mode = self.theme_combobox.currentIndex() == 1
        self.parent().dark_mode = dark_mode
        self.parent().settings.setValue("dark_mode", dark_mode)

        self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BrowserX()
    window.show()
    sys.exit(app.exec_())
