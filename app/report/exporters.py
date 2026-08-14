from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QImage,
    QPainter,
    QPageSize,
    QTextDocument,
)
from PySide6.QtPrintSupport import QPrinter

from app.report.models import ReportArtifact


def export_report(
    artifact: ReportArtifact,
    file_format: str,
    file_path: str,
):
    fmt = file_format.lower().strip()

    if fmt == "markdown":
        _write_text(
            file_path,
            artifact.markdown,
        )
        return

    if fmt == "html":
        _write_text(
            file_path,
            artifact.html,
        )
        return

    if fmt == "pdf":
        _export_pdf(
            artifact.html,
            file_path,
        )
        return

    if fmt == "png":
        _export_png(
            artifact.html,
            file_path,
        )
        return

    raise ValueError(
        f"不支持的报告格式：{file_format}"
    )


def _write_text(
    file_path: str,
    content: str,
):
    Path(file_path).write_text(
        content,
        encoding="utf-8",
    )


def _build_document(
    html_content: str,
) -> QTextDocument:
    document = QTextDocument()
    document.setDefaultStyleSheet("""
        body {
            font-family: "Microsoft YaHei";
            font-size: 11pt;
            color: #1f2937;
        }
        h1, h2, h3 {
            color: #111827;
        }
        table {
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #d1d5db;
            padding: 5px;
        }
        a {
            color: #2563eb;
        }
    """)
    document.setHtml(html_content)
    return document


def _export_pdf(
    html_content: str,
    file_path: str,
):
    printer = QPrinter(
        QPrinter.PrinterMode.HighResolution
    )
    printer.setOutputFormat(
        QPrinter.OutputFormat.PdfFormat
    )
    printer.setOutputFileName(
        file_path
    )
    printer.setPageSize(
        QPageSize(
            QPageSize.PageSizeId.A4
        )
    )

    document = _build_document(
        html_content
    )
    document.print_(printer)


def _export_png(
    html_content: str,
    file_path: str,
):
    document = _build_document(
        html_content
    )

    content_width = 1100
    margin = 40

    document.setTextWidth(
        content_width
    )

    size = document.size()

    width = int(
        content_width
        + margin * 2
    )
    height = max(
        500,
        int(size.height())
        + margin * 2,
    )

    # 防止异常模型输出生成极端尺寸图片。
    max_height = 30000
    height = min(
        height,
        max_height,
    )

    image = QImage(
        width,
        height,
        QImage.Format.Format_ARGB32,
    )
    image.fill(
        Qt.GlobalColor.white
    )

    painter = QPainter(image)
    painter.translate(
        margin,
        margin,
    )
    document.drawContents(painter)
    painter.end()

    if not image.save(file_path):
        raise RuntimeError(
            "PNG 保存失败。"
        )
