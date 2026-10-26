"""Sets the CV PDF's document properties, so recruiter systems and file search
label it by name and role. Called by scripts/cv_pdf.js after each render."""
import sys
from pypdf import PdfReader, PdfWriter

path = sys.argv[1]
w = PdfWriter(clone_from=PdfReader(path))
w.add_metadata({
    '/Title': 'Amber Lan · CV · AI marketing engineer and GTM engineer',
    '/Author': 'Amber Lan',
    '/Subject': 'CV of Amber Lan, AI marketing engineer and GTM engineer in Auckland, New Zealand',
    '/Keywords': 'Amber Lan, AI marketing engineer, GTM engineer, marketing engineer, product marketing, growth marketing, demand generation, ABM, AEO, SEO, HubSpot, Claude Code, Auckland, New Zealand',
})
with open(path, 'wb') as f:
    w.write(f)
