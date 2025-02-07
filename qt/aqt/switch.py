# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
from typing import cast

from aqt import colors
from aqt.qt import *
from aqt.theme import theme_manager


class Switch(QAbstractButton):
    """A horizontal slider to toggle between two states which can be denoted by short strings.

    The left state is the default and corresponds to isChecked()=False.
    The suppoorted slots are toggle(), for an animated transition, and setChecked().
    """

    def __init__(
        self,
        radius: int = 10,
        left_label: str = "",
        right_label: str = "",
        left_color: tuple[str, str] = colors.ACCENT_CARD,
        right_color: tuple[str, str] = colors.ACCENT_NOTE,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent=parent)
        self.setCheckable(True)
        super().setChecked(False)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._left_label = left_label
        self._right_label = right_label
        self._left_color = left_color
        self._right_color = right_color
        self._path_radius = radius
        self._knob_radius = radius - 1
        self._left_position = self._position = radius
        self._right_position = 3 * self._path_radius

    @pyqtProperty(int)  # type: ignore
    def position(self) -> int:
        return self._position

    @position.setter  # type: ignore
    def position(self, position: int) -> None:
        self._position = position
        self.update()

    @property
    def start_position(self) -> int:
        return self._left_position if self.isChecked() else self._right_position

    @property
    def end_position(self) -> int:
        return self._right_position if self.isChecked() else self._left_position

    @property
    def label(self) -> str:
        return self._right_label if self.isChecked() else self._left_label

    @property
    def path_color(self) -> QColor:
        color = self._right_color if self.isChecked() else self._left_color
        return theme_manager.qcolor(color)

    def sizeHint(self) -> QSize:
        return QSize(
            4 * self._path_radius,
            2 * self._path_radius,
        )

    def setChecked(self, checked: bool) -> None:
        super().setChecked(checked)
        self._position = self.end_position
        self.update()

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        self._paint_path(painter)
        self._paint_knob(painter)
        self._paint_label(painter)

    def _paint_path(self, painter: QPainter) -> None:
        painter.setBrush(QBrush(self.path_color))
        rectangle = QRectF(
            0,
            0,
            self.width(),
            self.height(),
        )
        painter.drawRoundedRect(rectangle, self._path_radius, self._path_radius)

    def _current_knob_rectangle(self) -> QRectF:
        return QRectF(
            self.position - self._knob_radius,  # type: ignore
            1,
            2 * self._knob_radius,
            2 * self._knob_radius,
        )

    def _paint_knob(self, painter: QPainter) -> None:
        color = theme_manager.qcolor(colors.BUTTON_GRADIENT_START)
        painter.setBrush(QBrush(color))
        painter.drawEllipse(self._current_knob_rectangle())

    def _paint_label(self, painter: QPainter) -> None:
        painter.setPen(theme_manager.qcolor(colors.FG))
        font = painter.font()
        font.setPixelSize(int(1.2 * self._knob_radius))
        painter.setFont(font)
        painter.drawText(
            self._current_knob_rectangle(), Qt.AlignmentFlag.AlignCenter, self.label
        )

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self._animate_toggle()

    def enterEvent(self, event: QEnterEvent) -> None:
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().enterEvent(event)

    def toggle(self) -> None:
        super().toggle()
        self._animate_toggle()

    def _animate_toggle(self) -> None:
        animation = QPropertyAnimation(self, cast(QByteArray, b"position"), self)
        animation.setDuration(100)
        animation.setStartValue(self.start_position)
        animation.setEndValue(self.end_position)
        # make triggered events execute first so the animation runs smoothly afterwards
        QTimer.singleShot(50, animation.start)
