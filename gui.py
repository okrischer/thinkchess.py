from PySide6.QtWidgets import (
  QDialog,
  QDialogButtonBox,
  QLabel,
  QVBoxLayout,
)

class Dialog(QDialog):
  def __init__(self, title: str, prompt: str) -> None:
    super().__init__()
    self.setWindowTitle(title)
    self.bb = QDialogButtonBox()
    self.bb.addButton(QDialogButtonBox.StandardButton.Ok)
    self.bb.addButton(QDialogButtonBox.StandardButton.Cancel)
    self.bb.accepted.connect(self.accept)
    self.bb.rejected.connect(self.reject)

    layout = QVBoxLayout()
    msg = QLabel(prompt)
    layout.addWidget(msg)
    layout.addWidget(self.bb)
    self.setLayout(layout)

