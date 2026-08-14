APP_STYLE = """
QMainWindow {
    background-color: #f5f6f8;
}

QWidget {
    font-family: "Microsoft YaHei";
}

#sidebar {
    background-color: #171a21;
}

#sidebarTitle {
    color: white;
    font-size: 20px;
    font-weight: bold;
}

#sidebarSubtitle {
    color: #8b93a1;
    font-size: 12px;
}

#navButton {
    background-color: transparent;
    color: #d0d4dc;
    border: none;
    text-align: left;
    padding: 12px 16px;
    border-radius: 6px;
    font-size: 15px;
}

#navButton:hover {
    background-color: #282d37;
    color: white;
}

#navButton:checked {
    background-color: #2d3440;
    color: white;
    font-weight: bold;
}

#versionLabel {
    color: #6e7684;
    font-size: 12px;
}

#pageTitle {
    color: #1c1e21;
    font-size: 28px;
    font-weight: bold;
}

#pageDescription {
    color: #666c76;
    font-size: 14px;
}

#card {
    background-color: white;
    border: 1px solid #e1e4e8;
    border-radius: 10px;
}

#cardTitle {
    color: #202328;
    font-size: 18px;
    font-weight: bold;
}

QCheckBox {
    font-size: 15px;
    color: #333333;
    spacing: 10px;
    min-width: 220px;
}

QLineEdit {
    background-color: white;
    color: #222222;
    border: 1px solid #d5d9df;
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 14px;
    min-height: 20px;
}

QLineEdit:focus {
    border: 1px solid #2563eb;
}

QComboBox {
    background-color: white;
    color: #222222;
    border: 1px solid #d5d9df;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 14px;
    min-height: 24px;
}

#primaryButton {
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 7px;
    padding: 10px 20px;
    font-size: 15px;
    font-weight: bold;
}

#primaryButton:hover {
    background-color: #1d4ed8;
}

#primaryButton:disabled {
    background-color: #94a3b8;
}

#secondaryButton {
    background-color: white;
    color: #333333;
    border: 1px solid #cfd4dc;
    border-radius: 7px;
    padding: 10px 20px;
    font-size: 14px;
}

#secondaryButton:hover {
    background-color: #f1f3f5;
}

#secondaryButton:disabled {
    color: #999999;
    background-color: #eeeeee;
}

#statusLabel {
    color: #666666;
    font-size: 14px;
}

QTextBrowser {
    background-color: white;
    border: none;
    font-size: 14px;
    padding: 5px;
}

#dangerButton {
    background-color: white;
    color: #b91c1c;
    border: 1px solid #fecaca;
    border-radius: 7px;
    padding: 8px 16px;
    font-size: 14px;
}

#dangerButton:hover {
    background-color: #fef2f2;
}

QListWidget, QTableWidget {
    background-color: white;
    border: 1px solid #e1e4e8;
    border-radius: 8px;
    font-size: 14px;
}

QListWidget::item {
    padding: 10px;
}

QListWidget::item:selected {
    background-color: #dbeafe;
    color: #1e3a8a;
}


QProgressBar {
    background-color: #eef2f7;
    border: 1px solid #d8dee8;
    border-radius: 6px;
    min-height: 12px;
    max-height: 12px;
}

QProgressBar::chunk {
    background-color: #2563eb;
    border-radius: 5px;
}

QDoubleSpinBox {
    background-color: white;
    color: #222222;
    border: 1px solid #d5d9df;
    border-radius: 6px;
    padding: 7px 10px;
    min-height: 22px;
}

QDoubleSpinBox:focus {
    border: 1px solid #2563eb;
}

QTabWidget::pane {
    border: 1px solid #e1e4e8;
    border-radius: 8px;
    background-color: white;
}

QTabBar::tab {
    padding: 8px 14px;
}

"""
