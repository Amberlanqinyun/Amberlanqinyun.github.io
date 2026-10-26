"""Sets the CV PDF's document properties, so recruiter systems and file search
label it by name and role. Called by scripts/cv_pdf.js after each render."""
import sys
from pypdf import PdfReader, PdfWriter

path = sys.argv[1]
META = {
    'en': {
        '/Title': 'Amber Lan · CV · AI marketing engineer and GTM engineer',
        '/Subject': 'CV of Amber Lan, AI marketing engineer and GTM engineer in Auckland, New Zealand',
        '/Keywords': 'Amber Lan, AI marketing engineer, GTM engineer, marketing engineer, product marketing, growth marketing, demand generation, ABM, AEO, SEO, HubSpot, Claude Code, Auckland, New Zealand',
    },
    'zh': {
        '/Title': 'Amber Lan · 简历 · AI 营销工程师与 GTM 工程师',
        '/Subject': 'Amber Lan 的简历：新西兰奥克兰的 AI 营销工程师与 GTM 工程师',
        '/Keywords': 'Amber Lan, AI 营销工程师, GTM 工程师, 营销工程师, 产品营销, 增长营销, 需求生成, ABM, AEO, SEO, HubSpot, Claude Code, 奥克兰, 新西兰',
    },
}
w = PdfWriter(clone_from=PdfReader(path))
w.add_metadata({'/Author': 'Amber Lan', **META['zh' if path.endswith('-zh.pdf') else 'en']})
with open(path, 'wb') as f:
    w.write(f)
