"""Build the submission deck: deck/index.html (JS + SVG) -> PNG overlays -> official template PPTX -> PDF.

Run from repo root:  py scripts/build_svg_deck.py
Needs Chrome, python-pptx, and PowerPoint (for the PDF export).
"""
import subprocess, pathlib
from pptx import Presentation
from pptx.util import Emu

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = (ROOT / 'deck' / 'index.html').as_uri()
OUT = ROOT / 'deck' / 'render'
TEMPLATE = ROOT / 'airtel_sync_case' / 'Submission Template_Sync.pptx'
NAME = 'Hacker_247_ABVIIITMGwalior'   # TeamName_CampusName, as the brief requires
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
import os
DECK = os.environ.get('DECK', '7')          # '7' = Unstop submission (7 slides); '9' = extended deck
N = int(DECK)

OUT.mkdir(exist_ok=True)
for i in range(1, N + 1):
    for bare, name in ((1, f'overlay{i}.png'), (0, f'slide{i}.png')):
        url = f'{HTML}?deck={DECK}&s={i}' + ('&bare=1' if bare else '')
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                        '--window-size=1920,1080', '--force-device-scale-factor=2',
                        '--default-background-color=00000000', '--virtual-time-budget=1500',
                        f'--screenshot={OUT / name}', url], check=True, capture_output=True)

prs = Presentation(TEMPLATE)
W, H = prs.slide_width, prs.slide_height
content_layout = prs.slides[1].slide_layout
bg2 = ROOT / 'deck' / 'assets' / 'tpl2.jpg'
for i in range(3, N + 1):            # template ships 2 slides; clone the content page for the rest
    s = prs.slides.add_slide(content_layout)
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    s.shapes.add_picture(str(bg2), 0, 0, W, H)
for i, s in enumerate(prs.slides, 1):
    s.shapes.add_picture(str(OUT / f'overlay{i}.png'), 0, 0, W, H)

# Slides are images, so add invisible clickable boxes over the cover's link lines.
# Coordinates are the 1920x1080 overlay space used in deck/index.html.
from pptx.enum.shapes import MSO_SHAPE
def link_box(slide, x, y, w, h, url):
    k = W / 1920
    b = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, int(x * k), int(y * k), int(w * k), int(h * k))
    b.fill.background(); b.line.fill.background(); b.shadow.inherit = False
    b.click_action.hyperlink.address = url
DEMO = 'https://youtu.be/ir74cLLgy4A'
link_box(prs.slides[0], 150, 976, 640, 28, 'https://vyaparsetu-airtel.vercel.app')
link_box(prs.slides[0], 600, 938, 360, 28, 'https://github.com/abhishekKokadwar/vyaparsetu')
link_box(prs.slides[0], 150, 1012, 460, 28, DEMO)

link_box(prs.slides[3], 1450, 258, 370, 19, 'https://vyaparsetu-airtel.vercel.app')
link_box(prs.slides[3], 1450, 278, 370, 19, DEMO)
link_box(prs.slides[N - 1], 1450, 236, 370, 19, 'https://vyaparsetu-airtel.vercel.app')
link_box(prs.slides[N - 1], 1450, 258, 370, 19, DEMO)

NAME = NAME if DECK == '7' else NAME + '_extended_9slides'
pptx = ROOT / f'{NAME}.pptx'
prs.save(pptx)
print('saved', pptx)

pdf = ROOT / f'{NAME}.pdf'
ps = (f"$p=New-Object -ComObject PowerPoint.Application;"
      f"$d=$p.Presentations.Open('{pptx}',$true,$false,$false);$d.SaveAs('{pdf}',32);$d.Close();$p.Quit()")
subprocess.run(['powershell', '-NoProfile', '-Command', ps], check=True)
print('saved', pdf)
