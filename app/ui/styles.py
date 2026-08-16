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


#mobileNav {
    background-color: #171a21;
    border-bottom: 1px solid #2d3440;
}

#mobileNavTitle {
    color: white;
    font-size: 16px;
    font-weight: bold;
}

#mobileNav QComboBox {
    background-color: #282d37;
    color: white;
    border: 1px solid #3b4350;
    min-width: 160px;
}


/* V0.9.1: Force readable combo-box popup colors.
   On some Windows palettes Qt inherited a dark popup background
   while keeping dark item text, which made the mobile navigation unreadable. */
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1f2937;
    border: 1px solid #cfd4dc;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
    outline: 0;
    padding: 4px;
}

QComboBox QAbstractItemView::item {
    min-height: 30px;
    padding: 5px 8px;
}

#mobileNav QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #111827;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

#mobileNav QComboBox {
    background-color: #282d37;
    color: #ffffff;
    border: 1px solid #4b5563;
    border-radius: 6px;
    padding: 7px 10px;
}

"""


MOBILE_STYLE = """
/* Android compact/touch UI overrides */

QWidget {
    font-size: 12px;
}

#pageTitle {
    font-size: 20px;
}

#pageDescription {
    font-size: 12px;
}

#cardTitle {
    font-size: 16px;
}

#statusLabel {
    font-size: 11px;
}

QCheckBox {
    font-size: 12px;
    min-width: 0px;
    spacing: 7px;
    color: #222222;
}

QCheckBox:checked {
    color: #222222;
}

QLineEdit {
    font-size: 12px;
    padding: 7px 9px;
    min-height: 20px;
}

QComboBox {
    font-size: 12px;
    padding: 6px 9px;
    min-height: 22px;
}

QDoubleSpinBox {
    font-size: 11px;
    padding: 6px 8px;
    min-height: 22px;
}

#primaryButton {
    font-size: 13px;
    padding: 9px 15px;
    min-height: 24px;
}

#secondaryButton {
    font-size: 12px;
    padding: 8px 12px;
    min-height: 22px;
}

QTextBrowser {
    font-size: 11px;
}

QListWidget,
QTableWidget {
    font-size: 10px;
}

QListWidget::item {
    padding: 7px;
}

QTabBar::tab {
    font-size: 11px;
    padding: 7px 10px;
}

#mobileNavTitle {
    font-size: 15px;
}

#mobileNav QComboBox {
    font-size: 13px;
    min-width: 145px;
    padding: 6px 8px;
    background-color: #282d37;
    color: #ffffff;
}

/* Android popup: never allow white text on white background. */
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #111827;
    selection-background-color: #dbeafe;
    selection-color: #111827;
}

QComboBox QAbstractItemView::item {
    color: #111827;
    background-color: #ffffff;
    min-height: 34px;
    padding: 5px 8px;
}

QComboBox QAbstractItemView::item:selected {
    color: #111827;
    background-color: #dbeafe;
}

#mobileNav QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #111827;
    selection-background-color: #dbeafe;
    selection-color: #111827;
}

#mobileNav QComboBox QAbstractItemView::item {
    color: #111827;
    background-color: #ffffff;
}

#mobileNav QComboBox QAbstractItemView::item:selected {
    color: #111827;
    background-color: #dbeafe;
}
"""


def get_app_style() -> str:
    from app.platform import is_android

    if is_android():
        return APP_STYLE + MOBILE_STYLE

    return APP_STYLE
