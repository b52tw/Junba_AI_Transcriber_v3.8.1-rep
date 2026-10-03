from __future__ import annotations

import argparse
import re
from pathlib import Path


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Junba AI Transcriber v3.8 source root")
    return ap.parse_args()


ROOT = Path(parse_args().root).resolve()


def read(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        raise SystemExit(f"找不到必要檔案：{rel}（ROOT={ROOT}）")
    return p.read_text(encoding="utf-8")


def write(rel: str, text: str) -> None:
    (ROOT / rel).write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f"套用修正失敗（找不到目標）：{label}")
    return text.replace(old, new, 1)


def sanity_check() -> None:
    required = [
        "main.py",
        "requirements.txt",
        "app/ui/main_window.py",
        "app/exporters/exporters.py",
        "app/core/worker.py",
        "JunbaAITranscriber_onefile.spec",
        "JunbaAITranscriber_portable.spec",
    ]
    missing = [x for x in required if not (ROOT / x).exists()]
    if missing:
        raise SystemExit("缺少必要檔案：" + ", ".join(missing))


def patch_main_window() -> None:
    rel = "app/ui/main_window.py"
    s = read(rel)

    s = replace_once(
        s,
        "self.review=QCheckBox('錄音核對播放器（KTV 同步＋可匯入 TXT/SRT/VTT）'); self.review.setChecked(True)",
        "self.review=QCheckBox('錄音核對播放器（KTV 同步＋可匯入 TXT/MD/SRT/VTT）'); self.review.setChecked(True)",
        "核對播放器格式",
    )

    s = replace_once(
        s,
        "outrow=QHBoxLayout(); self.output=QLineEdit(str(Path.home()/'Documents'/'JunbaTranscripts')); ob=QPushButton('選擇輸出位置'); ob.clicked.connect(self.choose_output); open_out=QPushButton('開啟輸出資料夾'); open_out.clicked.connect(self.open_output_folder); self.open_review_btn=QPushButton('開啟最新核對播放器'); self.open_review_btn.setEnabled(False); self.open_review_btn.clicked.connect(self.open_latest_review); outrow.addWidget(self.output,1); outrow.addWidget(ob); outrow.addWidget(open_out); outrow.addWidget(self.open_review_btn); root.addLayout(outrow)",
        "outrow=QHBoxLayout(); self.output=QLineEdit(str(Path.home()/'Documents'/'JunbaTranscripts')); ob=QPushButton('選擇輸出位置'); ob.clicked.connect(self.choose_output); open_out=QPushButton('開啟輸出資料夾'); open_out.clicked.connect(self.open_output_folder); self.open_review_btn=QPushButton('開啟／選擇核對播放器'); self.open_review_btn.setEnabled(True); self.open_review_btn.clicked.connect(self.open_latest_review); outrow.addWidget(self.output,1); outrow.addWidget(ob); outrow.addWidget(open_out); outrow.addWidget(self.open_review_btn); root.addLayout(outrow)",
        "核對播放器按鈕",
    )

    s = replace_once(
        s,
        "fmts=QHBoxLayout(); self.f_docx=QCheckBox('Word'); self.f_docx.setChecked(True); self.f_txt=QCheckBox('TXT'); self.f_txt.setChecked(True); self.f_srt=QCheckBox('SRT'); self.f_srt.setChecked(True); self.f_vtt=QCheckBox('VTT')\n        for x in (self.f_docx,self.f_txt,self.f_srt,self.f_vtt): fmts.addWidget(x)",
        "fmts=QHBoxLayout(); self.f_docx=QCheckBox('Word'); self.f_docx.setChecked(True); self.f_txt=QCheckBox('TXT'); self.f_txt.setChecked(True); self.f_md=QCheckBox('Markdown'); self.f_srt=QCheckBox('SRT'); self.f_srt.setChecked(True); self.f_vtt=QCheckBox('VTT')\n        for x in (self.f_docx,self.f_txt,self.f_md,self.f_srt,self.f_vtt): fmts.addWidget(x)",
        "Markdown 輸出選項",
    )

    pattern = re.compile(
        r"    def open_latest_review\(self\):\n.*?(?=    def refresh_hardware\(self, initial=False\):)",
        re.S,
    )
    new_method = '''    def open_latest_review(self):
        output_root = Path(self.output.text()).expanduser()
        latest = Path(self.latest_review_path) if self.latest_review_path else None

        if (not latest or not latest.exists()) and output_root.exists():
            try:
                found = sorted(
                    output_root.rglob('*_錄音核對.html'),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True,
                )
                latest = found[0] if found else None
            except Exception:
                latest = None

        if latest and latest.exists():
            box = QMessageBox(self)
            box.setWindowTitle('錄音核對播放器')
            box.setText(f'最近的核對播放器：\\n{latest.name}')
            open_latest = box.addButton('開啟最近', QMessageBox.AcceptRole)
            choose_other = box.addButton('選擇其他檔案…', QMessageBox.ActionRole)
            box.addButton('取消', QMessageBox.RejectRole)
            box.exec()
            if box.clickedButton() is open_latest:
                self.latest_review_path = str(latest)
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(latest)))
                return
            if box.clickedButton() is not choose_other:
                return

        start_dir = str(
            latest.parent if latest and latest.exists()
            else (output_root if output_root.exists() else Path.home())
        )
        selected, _ = QFileDialog.getOpenFileName(
            self,
            '選擇錄音核對播放器',
            start_dir,
            '核對播放器 (*.html *.htm);;所有檔案 (*.*)',
        )
        if selected:
            self.latest_review_path = selected
            QDesktopServices.openUrl(QUrl.fromLocalFile(selected))

'''
    if pattern.search(s):
        s = pattern.sub(new_method, s, count=1)
    elif "選擇其他檔案…" not in s:
        raise SystemExit("套用修正失敗：open_latest_review")

    s = replace_once(
        s,
        "if self.f_txt.isChecked():formats.append('txt')\n        if self.f_srt.isChecked():formats.append('srt')",
        "if self.f_txt.isChecked():formats.append('txt')\n        if self.f_md.isChecked():formats.append('md')\n        if self.f_srt.isChecked():formats.append('srt')",
        "Markdown 格式加入工作",
    )

    write(rel, s)


def patch_exporters() -> None:
    rel = "app/exporters/exporters.py"
    s = read(rel)

    s = replace_once(
        s,
        "from docx.shared import Inches",
        "from docx.shared import Inches, Pt\nfrom docx.enum.section import WD_ORIENT",
        "Word 匯入",
    )

    s = replace_once(
        s,
        'accept=".txt,.srt,.vtt,.json,text/plain,text/vtt,application/json"',
        'accept=".txt,.md,.markdown,.srt,.vtt,.json,text/plain,text/markdown,text/vtt,application/json"',
        "播放器 Markdown 載入",
    )
    s = s.replace(
        "SRT/VTT 會保留原本時間碼；TXT／貼上文字會依原始逐字稿段落順序自動估算時間。",
        "SRT/VTT 會保留原本時間碼；TXT/Markdown／貼上文字會依原始逐字稿段落順序自動估算時間。",
    )

    marker = """        p.write_text(body, encoding='utf-8-sig')
        out.append(str(p))
    if 'srt' in formats and result.segments:
"""
    md_block = """        p.write_text(body, encoding='utf-8-sig')
        out.append(str(p))
    if 'md' in formats:
        p = base.with_suffix('.md')
        lines = [f'# {base.stem}', '', f'- 辨識引擎：{result.engine}']
        if result.language:
            lines.append(f'- 語言：{result.language}')
        if source_audio:
            lines.append(f'- 來源音檔：{Path(source_audio).name}')
        if note:
            lines += ['', f'> {note}']
        lines += ['', '## 時間軸逐字稿', '']
        if result.segments:
            for s in result.segments:
                end = s.end if s.end > s.start else s.start + 2.0
                speaker = f'{s.speaker}：' if s.speaker else ''
                lines.append(f'- **[{_time_label(s.start)}–{_time_label(end)}]** {speaker}{s.text}')
        elif result.text:
            lines.append(result.text)
        if result.segments and result.text:
            timeline_text = '\\n'.join(_line(x) for x in result.segments).strip()
            cleaned = result.text.strip()
            if cleaned and cleaned != timeline_text:
                lines += ['', '## AI 整理後全文（參考）', '', cleaned]
        p.write_text('\\n'.join(lines) + '\\n', encoding='utf-8-sig')
        out.append(str(p))
    if 'srt' in formats and result.segments:
"""
    s = replace_once(s, marker, md_block, "Markdown 匯出")

    s = replace_once(
        s,
        "        doc = Document()\n        doc.add_heading(base.stem, level=1)",
        """        doc = Document()
        section = doc.sections[0]
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width, section.page_height = section.page_height, section.page_width
        section.top_margin = Inches(0.55)
        section.bottom_margin = Inches(0.55)
        section.left_margin = Inches(0.55)
        section.right_margin = Inches(0.55)
        doc.add_heading(base.stem, level=1)""",
        "Word 橫向版面",
    )

    s = replace_once(
        s,
        "            widths = (Inches(1.35), Inches(0.9), Inches(4.55))",
        "            widths = (Inches(1.45), Inches(0.70), Inches(8.10))",
        "Word 欄寬",
    )

    row_marker = """                row[0].text = f'{_time_label(s.start)}–{_time_label(end)}'
                row[1].text = s.speaker or ''
                row[2].text = s.text
"""
    row_new = """                row[0].text = f'{_time_label(s.start)}–{_time_label(end)}'
                row[1].text = s.speaker or ''
                row[2].text = s.text
                for cell in (row[0], row[1]):
                    for para in cell.paragraphs:
                        for run in para.runs:
                            run.font.size = Pt(9)
                for para in row[2].paragraphs:
                    for run in para.runs:
                        run.font.size = Pt(11)
"""
    s = replace_once(s, row_marker, row_new, "Word 逐字內容字體")

    write(rel, s)


def patch_worker() -> None:
    rel = "app/core/worker.py"
    s = read(rel)

    s = replace_once(
        s,
        "                srcp = Path(source)\n                with self._activity_lock:",
        """                srcp = Path(source)
                self._current_output_dir = self.output_dir / f'{fi + 1:02d}_{srcp.stem}'
                self._current_output_dir.mkdir(parents=True, exist_ok=True)
                with self._activity_lock:""",
        "逐檔輸出資料夾",
    )

    s = replace_once(
        s,
        "        base = self.output_dir / f'{srcp.stem}{suffix}'",
        """        file_out_dir = Path(getattr(self, '_current_output_dir', self.output_dir / srcp.stem))
        file_out_dir.mkdir(parents=True, exist_ok=True)
        base = file_out_dir / f'{srcp.stem}{suffix}'""",
        "匯出基底資料夾",
    )

    write(rel, s)


if __name__ == "__main__":
    sanity_check()
    patch_main_window()
    patch_exporters()
    patch_worker()
    print(f"v3.8.1 patch applied successfully: {ROOT}")
