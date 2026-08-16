from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QFrame,
    QLayout,
    QScrollArea,
    QScroller,
    QWidget,
)


def enable_touch_scrolling(
    root: QWidget,
):
    """
    Enable native touch-drag / kinetic scrolling for every Qt
    scroll viewport below root.

    Desktop callers may safely skip this helper.
    """
    areas: list[QAbstractScrollArea] = []

    if isinstance(
        root,
        QAbstractScrollArea,
    ):
        areas.append(root)

    areas.extend(
        root.findChildren(
            QAbstractScrollArea
        )
    )

    seen: set[int] = set()

    for area in areas:
        marker = id(area)

        if marker in seen:
            continue

        seen.add(marker)

        viewport = area.viewport()

        if viewport is None:
            continue

        try:
            viewport.setAttribute(
                Qt.WidgetAttribute.WA_AcceptTouchEvents,
                True,
            )

            QScroller.grabGesture(
                viewport,
                QScroller.ScrollerGestureType.TouchGesture,
            )
        except Exception:
            # Scrolling enhancement must never break app startup.
            continue


def wrap_mobile_page(
    page: QWidget,
) -> QScrollArea:
    """
    Put a normal desktop-style page inside a vertically scrollable
    Android viewport.

    The page remains the data/logic object; only the object inserted
    into QStackedWidget is the wrapper.
    """
    layout = page.layout()

    if layout is not None:
        try:
            layout.setSizeConstraint(
                QLayout.SizeConstraint.SetMinimumSize
            )
        except Exception:
            pass

    scroll = QScrollArea()
    scroll.setObjectName(
        "mobilePageScroll"
    )
    scroll.setFrameShape(
        QFrame.Shape.NoFrame
    )
    scroll.setWidgetResizable(
        True
    )
    scroll.setHorizontalScrollBarPolicy(
        Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )
    scroll.setVerticalScrollBarPolicy(
        Qt.ScrollBarPolicy.ScrollBarAsNeeded
    )
    scroll.setWidget(
        page
    )

    enable_touch_scrolling(
        scroll
    )

    return scroll
