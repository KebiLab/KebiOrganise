"""
KebiOrganise GUI - File Organizer Application
Author: KebiLab
Version: 1.0.0
"""

import logging
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

warnings.filterwarnings("ignore", category=DeprecationWarning)

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QProgressBar,
)
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.uic import loadUi

FILE_CATEGORIES: Dict[str, List[str]] = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".ico"],
    "Documents": [
        ".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt",
        ".xlsx", ".xls", ".csv", ".pptx", ".pptm"
    ],
    "Audio": [".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"],
    "Video": [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Executables": [".exe", ".msi", ".apk", ".bat", ".sh"],
}

CATEGORY_NAMES_EN: Dict[str, str] = {
    "Images": "Images",
    "Documents": "Documents",
    "Audio": "Audio",
    "Video": "Video",
    "Archives": "Archives",
    "Executables": "Executables",
    "Others": "Others",
}

CATEGORY_NAMES_RU: Dict[str, str] = {
    "Images": "Изображения",
    "Documents": "Документы",
    "Audio": "Аудио",
    "Video": "Видео",
    "Archives": "Архивы",
    "Executables": "Программы",
    "Others": "Прочее",
}

LOG_FILENAME: str = "organizer_log.txt"
SCRIPT_NAME: str = "main.py"

TRANSLATIONS = {
    "ru": {
        "window_title": "KebiOrganise - Сортировка файлов",
        "logo": "KebiOrganise",
        "made_by": "Made by KebiLab",
        "language_label": "Язык",
        "theme_label": "Тема",
        "selected_folder": "Выбранная папка:",
        "no_folder": "Папка не выбрана",
        "browse": "Обзор",
        "categories_title": "Категории файлов",
        "images": "Изображения:",
        "documents": "Документы:",
        "audio": "Аудио:",
        "video": "Видео:",
        "archives": "Архивы:",
        "executables": "Программы:",
        "others": "Прочее:",
        "all_others": "Все остальные файлы",
        "progress_title": "Прогресс",
        "ready": "Готов",
        "log_title": "Журнал операций",
        "organize": "Сортировать файлы",
        "clear_log": "Очистить журнал",
        "exit": "Выход",
        "warning_no_folder": "Пожалуйста, выберите папку для сортировки файлов.",
        "warning_title": "Предупреждение",
        "initializing": "Инициализация...",
        "scanning": "Сканирование файлов...",
        "processing": "Обработка: ",
        "sorting_complete": "Сортировка завершена",
        "log_cleared": "Журнал очищен",
        "exit_confirm": "Вы действительно хотите выйти из приложения?",
        "exit_title": "Выход",
        "sorting_in_progress": "Сортировка ещё не завершена. Вы действительно хотите выйти?",
        "confirm_title": "Подтверждение",
        "folder_selected": "Папка выбрана: ",
        "organize_complete": "Сортировка файлов завершена.",
        "moved_files": "Перемещено файлов: ",
        "errors": "Ошибок: ",
        "log_saved": "Лог сохранён в: ",
        "complete_title": "Сортировка завершена",
        "theme_light": "Светлая",
        "theme_dark": "Тёмная",
        "theme_system": "Системная",
        "lang_ru": "Русский",
        "lang_en": "English",
        "folder_dialog_title": "Выберите папку для сортировки файлов",
    },
    "en": {
        "window_title": "KebiOrganise - File Organizer",
        "logo": "KebiOrganise",
        "made_by": "Made by KebiLab",
        "language_label": "Language",
        "theme_label": "Theme",
        "selected_folder": "Selected Folder:",
        "no_folder": "No folder selected",
        "browse": "Browse",
        "categories_title": "File Categories",
        "images": "Images:",
        "documents": "Documents:",
        "audio": "Audio:",
        "video": "Video:",
        "archives": "Archives:",
        "executables": "Executables:",
        "others": "Others:",
        "all_others": "All other file extensions",
        "progress_title": "Progress",
        "ready": "Ready",
        "log_title": "Activity Log",
        "organize": "Organize Files",
        "clear_log": "Clear Log",
        "exit": "Exit",
        "warning_no_folder": "Please select a folder to organize files.",
        "warning_title": "Warning",
        "initializing": "Initializing...",
        "scanning": "Scanning files...",
        "processing": "Processing: ",
        "sorting_complete": "Sorting complete",
        "log_cleared": "Log cleared",
        "exit_confirm": "Do you really want to exit the application?",
        "exit_title": "Exit",
        "sorting_in_progress": "Sorting is not yet complete. Do you really want to exit?",
        "confirm_title": "Confirm",
        "folder_selected": "Folder selected: ",
        "organize_complete": "File sorting completed.",
        "moved_files": "Files moved: ",
        "errors": "Errors: ",
        "log_saved": "Log saved to: ",
        "complete_title": "Sorting Complete",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "theme_system": "System",
        "lang_ru": "Русский",
        "lang_en": "English",
        "folder_dialog_title": "Select folder to organize files",
    },
}

LIGHT_THEME = """
QMainWindow {
    background-color: #f5f5f5;
}
QFrame#headerFrame {
    background-color: #2196F3;
    padding: 10px;
}
QLabel#logoLabel {
    color: #ffffff;
    font-size: 18px;
    font-weight: bold;
}
QLabel#kibiLabLabel {
    color: #e3f2fd;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #bdbdbd;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QPushButton {
    background-color: #2196F3;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #1976D2;
}
QPushButton:pressed {
    background-color: #0D47A1;
}
QPushButton:disabled {
    background-color: #bdbdbd;
}
QLineEdit {
    border: 1px solid #bdbdbd;
    border-radius: 4px;
    padding: 8px;
    background-color: #ffffff;
    color: #000000;
    min-height: 24px;
}
QPlainTextEdit {
    border: 1px solid #bdbdbd;
    border-radius: 4px;
    background-color: #ffffff;
    color: #000000;
    font-family: Consolas;
}
QProgressBar {
    border: 1px solid #bdbdbd;
    border-radius: 4px;
    text-align: center;
    background-color: #ffffff;
    color: #000000;
}
QProgressBar::chunk {
    background-color: #2196F3;
}
QComboBox {
    border: 1px solid #bdbdbd;
    border-radius: 4px;
    padding: 8px;
    background-color: #ffffff;
    color: #000000;
    min-height: 24px;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #757575;
    margin-right: 5px;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #bdbdbd;
    selection-background-color: #2196F3;
    selection-color: #ffffff;
    outline: none;
}
QComboBox QAbstractItemView::item {
    min-height: 30px;
    padding: 5px;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #2196F3;
    color: #ffffff;
}
QComboBox::item:selected {
    background-color: #2196F3;
    color: #ffffff;
}
QStatusBar {
    background-color: #e0e0e0;
}
"""

DARK_THEME = """
QMainWindow {
    background-color: #1e1e1e;
}
QFrame#headerFrame {
    background-color: #2d2d2d;
    padding: 10px;
}
QLabel#logoLabel {
    color: #4fc3f7;
    font-size: 18px;
    font-weight: bold;
}
QLabel#kibiLabLabel {
    color: #90a4ae;
}
QLabel {
    color: #e0e0e0;
}
QGroupBox {
    font-weight: bold;
    color: #e0e0e0;
    border: 1px solid #424242;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #4fc3f7;
}
QPushButton {
    background-color: #0288D1;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #039BE5;
}
QPushButton:pressed {
    background-color: #01579B;
}
QPushButton:disabled {
    background-color: #424242;
    color: #757575;
}
QLineEdit {
    border: 1px solid #424242;
    border-radius: 4px;
    padding: 10px;
    background-color: #3d3d3d;
    color: #ffffff;
    selection-background-color: #0288D1;
    min-height: 24px;
}
QPlainTextEdit {
    border: 1px solid #424242;
    border-radius: 4px;
    background-color: #2d2d2d;
    color: #ffffff;
    font-family: Consolas;
    selection-background-color: #0288D1;
}
QProgressBar {
    border: 1px solid #424242;
    border-radius: 4px;
    text-align: center;
    background-color: #2d2d2d;
    color: #ffffff;
}
QProgressBar::chunk {
    background-color: #0288D1;
}
QComboBox {
    border: 1px solid #424242;
    border-radius: 4px;
    padding: 8px;
    background-color: #3d3d3d;
    color: #ffffff;
    selection-background-color: #0288D1;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #90a4ae;
    margin-right: 5px;
}
QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #424242;
    selection-background-color: #0288D1;
    selection-color: #ffffff;
    outline: none;
}
QComboBox QAbstractItemView::item {
    min-height: 30px;
    padding: 5px;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #0288D1;
    color: #ffffff;
}
QComboBox::item:selected {
    background-color: #0288D1;
    color: #ffffff;
}
QStatusBar {
    background-color: #2d2d2d;
    color: #e0e0e0;
}
"""


class OrganizerSignals(QObject):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    log_message = pyqtSignal(str)
    finished = pyqtSignal(dict, int, int)
    error = pyqtSignal(str)


class OrganizerWorker(QThread):

    def __init__(
        self,
        root_path: Path,
        signals: OrganizerSignals,
        category_names: Dict[str, str]
    ):
        super().__init__()
        self.root_path = root_path
        self.signals = signals
        self.category_names = category_names
        self.moved_count = 0
        self.error_count = 0
        self.report: Dict[str, List[str]] = {
            category: [] for category in CATEGORY_NAMES_EN
        }

    def _get_category_for_extension(self, extension: str) -> str:
        ext_lower = extension.lower()
        for category, extensions in FILE_CATEGORIES.items():
            if ext_lower in extensions:
                return category
        return "Others"

    def _generate_unique_filename(self, dest_path: Path) -> Path:
        if not dest_path.exists():
            return dest_path
        stem = dest_path.stem
        suffix = dest_path.suffix
        parent = dest_path.parent
        index = 1
        while True:
            new_name = f"{stem}_{index}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            index += 1

    def _move_file(self, file_path: Path, category: str) -> bool:
        target_folder = self.root_path / self.category_names[category]
        target_folder.mkdir(parents=True, exist_ok=True)
        dest_path = target_folder / file_path.name
        dest_path = self._generate_unique_filename(dest_path)
        try:
            file_path.rename(dest_path)
            self.report[category].append(file_path.name)
            self.moved_count += 1
            self.signals.log_message.emit(
                f"[OK] Moved: {file_path.name} -> {self.category_names[category]}/"
            )
            return True
        except PermissionError:
            self.signals.log_message.emit(
                f"[ERROR] File locked: {file_path.name}"
            )
            self.error_count += 1
            return False
        except OSError as e:
            self.signals.log_message.emit(
                f"[ERROR] Move error {file_path.name}: {e}"
            )
            self.error_count += 1
            return False

    def run(self) -> None:
        self.signals.status.emit(self.tr("Scanning files..."))
        self.signals.log_message.emit(f"Starting sort in folder: {self.root_path}")
        self.signals.log_message.emit("=" * 50)
        files_to_process: List[Path] = []
        for item in self.root_path.iterdir():
            if item.is_dir():
                continue
            if item.name == SCRIPT_NAME:
                self.signals.log_message.emit(f"[SKIP] Script file: {item.name}")
                continue
            if item.name == LOG_FILENAME:
                continue
            if item.is_file():
                files_to_process.append(item)
        files_to_process.sort(key=lambda x: x.name.lower())
        total_files = len(files_to_process)
        if total_files == 0:
            self.signals.status.emit("No files to sort")
            self.signals.log_message.emit("No files to process")
            self.signals.finished.emit(self.report, 0, 0)
            return
        for index, file_path in enumerate(files_to_process, 1):
            extension = file_path.suffix
            category = self._get_category_for_extension(extension)
            progress = int((index / total_files) * 100)
            self.signals.progress.emit(progress)
            self.signals.status.emit(
                f"Processing: {file_path.name} ({index}/{total_files})"
            )
            self._move_file(file_path, category)
        self.signals.log_message.emit("=" * 50)
        self.signals.log_message.emit(
            f"Sorting complete. Files moved: {self.moved_count}"
        )
        self.signals.status.emit("Sorting complete")
        self.signals.finished.emit(self.report, self.moved_count, self.error_count)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.current_language = "ru"
        self.current_theme = "light"
        loadUi("main.ui", self)
        self.selected_path: Optional[Path] = None
        self.worker: Optional[OrganizerWorker] = None
        self.signals: Optional[OrganizerSignals] = None
        self._init_comboboxes()
        self._connect_signals()
        self._apply_translations()
        self._setup_logging()

    def _init_comboboxes(self) -> None:
        self.languageCombo.addItem(TRANSLATIONS["ru"]["lang_ru"], "ru")
        self.languageCombo.addItem(TRANSLATIONS["ru"]["lang_en"], "en")
        self.languageCombo.setCurrentIndex(0)
        self.themeCombo.addItem(TRANSLATIONS["ru"]["theme_light"], "light")
        self.themeCombo.addItem(TRANSLATIONS["ru"]["theme_dark"], "dark")
        self.themeCombo.addItem(TRANSLATIONS["ru"]["theme_system"], "system")
        self.themeCombo.setCurrentIndex(0)
        self.languageCombo.currentIndexChanged.connect(self._on_language_changed)
        self.themeCombo.currentIndexChanged.connect(self._on_theme_changed)

    def _connect_signals(self) -> None:
        self.browseButton.clicked.connect(self._on_browse_clicked)
        self.organizeButton.clicked.connect(self._on_organize_clicked)
        self.clearLogButton.clicked.connect(self._on_clear_log_clicked)
        self.exitButton.clicked.connect(self._on_exit_clicked)

    def _setup_logging(self) -> None:
        self.logger = logging.getLogger("KebiOrganiseGUI")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()

    def _log_to_widget(self, message: str) -> None:
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self.logText.appendPlainText(f"[{timestamp}] {message}")

    def _get_translation(self, key: str) -> str:
        return TRANSLATIONS.get(self.current_language, {}).get(key, key)

    def _apply_translations(self) -> None:
        t = self._get_translation
        self.setWindowTitle(t("window_title"))
        self.logoLabel.setText(t("logo"))
        self.kibiLabLabel.setText(t("made_by"))
        self.folderLabel.setText(t("selected_folder"))
        self.folderPathEdit.setPlaceholderText(t("no_folder"))
        self.browseButton.setText(t("browse"))
        self.categoriesGroup.setTitle(t("categories_title"))
        self.imagesLabel.setText(t("images"))
        self.documentsLabel.setText(t("documents"))
        self.audioLabel.setText(t("audio"))
        self.videoLabel.setText(t("video"))
        self.archivesLabel.setText(t("archives"))
        self.executablesLabel.setText(t("executables"))
        self.othersLabel.setText(t("others"))
        self.othersEdit.setText(t("all_others"))
        self.progressGroup.setTitle(t("progress_title"))
        self.statusLabel.setText(t("ready"))
        self.logGroup.setTitle(t("log_title"))
        self.organizeButton.setText(t("organize"))
        self.clearLogButton.setText(t("clear_log"))
        self.exitButton.setText(t("exit"))
        self.languageCombo.setToolTip(t("language_label"))
        self.themeCombo.setToolTip(t("theme_label"))

    def _on_language_changed(self, index: int) -> None:
        language_code = self.languageCombo.itemData(index)
        if language_code:
            self.current_language = language_code
            theme_index = self.themeCombo.currentIndex()
            self.themeCombo.clear()
            t = self._get_translation
            self.themeCombo.addItem(t("theme_light"), "light")
            self.themeCombo.addItem(t("theme_dark"), "dark")
            self.themeCombo.addItem(t("theme_system"), "system")
            self.themeCombo.setCurrentIndex(theme_index)
            self._apply_translations()
            self._log_to_widget(f"Language changed to: {language_code}")

    def _on_theme_changed(self, index: int) -> None:
        theme_code = self.themeCombo.itemData(index)
        if theme_code:
            self.current_theme = theme_code
            self._apply_theme(theme_code)
            self._log_to_widget(f"Theme changed to: {theme_code}")

    def _apply_theme(self, theme: str) -> None:
        if theme == "light":
            self.setStyleSheet(LIGHT_THEME)
        elif theme == "dark":
            self.setStyleSheet(DARK_THEME)
        else:
            self.setStyleSheet("")

    def _on_browse_clicked(self) -> None:
        folder_path = QFileDialog.getExistingDirectory(
            self,
            self._get_translation("folder_dialog_title"),
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder_path:
            self.selected_path = Path(folder_path)
            self.folderPathEdit.setText(folder_path)
            self._log_to_widget(f"Folder selected: {folder_path}")
            self.statusbar.showMessage(
                self._get_translation("folder_selected") + folder_path,
                5000
            )

    def _on_organize_clicked(self) -> None:
        if self.selected_path is None:
            QMessageBox.warning(
                self,
                self._get_translation("warning_title"),
                self._get_translation("warning_no_folder")
            )
            return
        self.organizeButton.setEnabled(False)
        self.browseButton.setEnabled(False)
        self.progressBar.setValue(0)
        self.statusLabel.setText(self._get_translation("initializing"))
        self.logText.clear()
        self.signals = OrganizerSignals()
        category_names = (
            CATEGORY_NAMES_RU
            if self.current_language == "ru"
            else CATEGORY_NAMES_EN
        )
        self.worker = OrganizerWorker(
            self.selected_path,
            self.signals,
            category_names
        )
        self.signals.progress.connect(self.progressBar.setValue)
        self.signals.status.connect(self.statusLabel.setText)
        self.signals.log_message.connect(self._log_to_widget)
        self.signals.finished.connect(self._on_organize_finished)
        self.signals.error.connect(self._on_organize_error)
        self._log_to_widget("Starting sort...")
        self.worker.start()

    def _on_organize_finished(
        self,
        report: Dict[str, List[str]],
        moved_count: int,
        error_count: int
    ) -> None:
        self.organizeButton.setEnabled(True)
        self.browseButton.setEnabled(True)
        self.progressBar.setValue(100)
        t = self._get_translation
        self._log_to_widget("=" * 50)
        self._log_to_widget("FINAL REPORT")
        self._log_to_widget("=" * 50)
        category_names = (
            CATEGORY_NAMES_RU
            if self.current_language == "ru"
            else CATEGORY_NAMES_EN
        )
        for category, files in report.items():
            if files:
                self._log_to_widget(
                    f"{category_names[category]}: {len(files)} file(s)"
                )
        self._log_to_widget("=" * 50)
        self._log_to_widget(f"Total moved: {moved_count}")
        if error_count > 0:
            self._log_to_widget(f"Errors: {error_count}")
        self._save_log_to_file()
        self.statusbar.showMessage(
            t("sorting_complete") + f". {t('moved_files')}{moved_count}",
            10000
        )
        QMessageBox.information(
            self,
            t("complete_title"),
            f"{t('organize_complete')}\n\n"
            f"{t('moved_files')}{moved_count}\n"
            f"{t('errors')}{error_count}\n\n"
            f"{t('log_saved')} {self.selected_path / LOG_FILENAME}"
        )

    def _on_organize_error(self, error_message: str) -> None:
        self.organizeButton.setEnabled(True)
        self.browseButton.setEnabled(True)
        self._log_to_widget(f"CRITICAL ERROR: {error_message}")
        QMessageBox.critical(
            self,
            "Error",
            f"An error occurred during sorting:\n{error_message}"
        )

    def _on_clear_log_clicked(self) -> None:
        self.logText.clear()
        self._log_to_widget(self._get_translation("log_cleared"))
        self.statusbar.showMessage(self._get_translation("log_cleared"), 3000)

    def _on_exit_clicked(self) -> None:
        if self.worker is not None and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                self._get_translation("confirm_title"),
                self._get_translation("sorting_in_progress"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        reply = QMessageBox.question(
            self,
            self._get_translation("exit_title"),
            self._get_translation("exit_confirm"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.close()

    def _save_log_to_file(self) -> None:
        if self.selected_path is None:
            return
        log_path = self.selected_path / LOG_FILENAME
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(self.logText.toPlainText())
        except OSError as e:
            self._log_to_widget(f"Log write error: {e}")

    def closeEvent(self, event) -> None:
        try:
            if self.worker is not None and self.worker.isRunning():
                reply = QMessageBox.question(
                    self,
                    self._get_translation("confirm_title"),
                    self._get_translation("sorting_in_progress"),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    event.ignore()
                    return
            self._log_to_widget("Application closed")
        except Exception:
            pass
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
