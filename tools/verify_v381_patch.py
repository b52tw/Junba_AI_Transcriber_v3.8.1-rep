from pathlib import Path
import argparse

ap=argparse.ArgumentParser(); ap.add_argument('--root', required=True); a=ap.parse_args()
r=Path(a.root)
checks={
 'app/ui/main_window.py': ['開啟／選擇核對播放器', "QCheckBox('Markdown')", "formats.append('md')", '選擇其他檔案…'],
 'app/exporters/exporters.py': ['WD_ORIENT.LANDSCAPE', "if 'md' in formats:", 'Inches(8.10)', 'Pt(11)', '.markdown'],
 'app/core/worker.py': ["f'{fi + 1:02d}_{srcp.stem}'", "_current_output_dir"],
}
for rel, needles in checks.items():
    text=(r/rel).read_text(encoding='utf-8')
    for n in needles:
        assert n in text, f'{rel} missing {n}'
print('PATCH_VERIFY_OK')
