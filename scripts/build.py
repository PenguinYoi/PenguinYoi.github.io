"""Render escaped CMS content into the public portfolio. Standard library only."""
from pathlib import Path
from html import escape
from string import Template
from urllib.parse import urlsplit
import hashlib, json, re, shutil

ROOT = Path(__file__).resolve().parents[1]

def text(value):
    if value is None: return ''
    if not isinstance(value, str): raise ValueError('Text fields must contain strings')
    return escape(value, quote=True)

def paragraphs(value, cls=''):
    if not value: return ''
    return ''.join(f'<p class="{cls}">{text(part)}</p>' for part in value.split('\n\n') if part.strip())

def url(value):
    if not isinstance(value, str) or not value or any(c.isspace() or ord(c) < 32 for c in value):
        raise ValueError('Links must be nonempty URLs without whitespace')
    parsed = urlsplit(value)
    if parsed.scheme:
        if parsed.scheme not in ('https', 'http', 'mailto'): raise ValueError('Unsupported URL scheme')
        if parsed.scheme in ('https', 'http') and not parsed.netloc: raise ValueError('Invalid web URL')
    elif value.startswith(('//', '\\')) or '\\' in value or ':' in value or '..' in parsed.path.split('/'):
        raise ValueError('Unsafe relative URL')
    return text(value)

def links(items):
    return '<div class="entry-links">'+''.join(f'<a href="{url(i["url"])}">{text(i["label"])}</a>' for i in items)+'</div>' if items else ''

def render(data):
    a, c = data['about'], data['contact']
    resume, github = url(c['resume']), url(c['github'])
    email = c['email']
    if not re.fullmatch(r'[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+', email): raise ValueError('Invalid email address')
    opening = f'''<section class="opening" aria-labelledby="opening-title"><div class="opening-main">
<p class="eyebrow">{text(a['eyebrow'])}</p><h1 id="opening-title">{text(a['headline'])}<br><em>{text(a['headline_emphasis'])}</em></h1>
<p class="opening-deck">{text(a['introduction'])}</p>{paragraphs(a['bio'],'opening-bio')}</div>
<aside class="margin-note" aria-label="At a glance"><div><p class="note-label">Currently</p>{paragraphs(a['current_note'])}</div><div><p class="note-label">Previously</p>{paragraphs(a['previous_note'])}</div><div><p class="note-label">Elsewhere</p><a href="{github}">GitHub</a></div></aside></section>'''
    projects = []
    ids = {'main','opening-title','work','work-title','about','about-title','contact'}
    for p in data['projects']['items']:
        anchor = p['id']
        if not re.fullmatch('[a-z][a-z0-9-]*',anchor) or anchor in ids: raise ValueError('Project IDs must be unique lowercase anchors')
        ids.add(anchor)
        status = f'<span class="status">{text(p.get("status",""))}</span>' if p.get('status') else ''
        topics = '<br>'.join(text(t) for t in p.get('topics',[]))
        notes = []
        for key,label in [('approach','The approach'),('question','The open question')]:
            if p.get(key): notes.append(f'<div><h4>{label}</h4>{paragraphs(p[key])}</div>')
        notes_html = '<div class="research-notes">'+''.join(notes)+'</div>' if notes else ''
        limits = '<details><summary>A note on interpreting the project</summary>'+paragraphs(p['limitations'])+'</details>' if p.get('limitations') else ''
        projects.append(f'''<article id="{text(anchor)}" class="entry {'featured' if p.get('featured') else ''} reveal"><aside class="entry-meta"><p class="note-label">{text(p.get('context',''))}</p><p class="project-name">{text(p['name'])}</p>{status}<p class="meta-topic">{topics}</p></aside><div class="entry-body"><h3>{text(p['title'])}</h3>{paragraphs(p.get('lead',''),'entry-lead')}{paragraphs(p['description'])}{links(p.get('links',[]))}{notes_html}{limits}</div></article>''')
    experience = ''.join(f'''<article><p class="note-label">{text(e['date'])}</p><div><h3>{text(e['organization'])}</h3><p class="role">{text(e['role'])}</p>{paragraphs(e['description'])}</div></article>''' for e in data['experience']['items'])
    about_paragraphs = ''.join(paragraphs(p) for p in a['about_paragraphs'])
    skills = '<br>'.join(text(s) for s in a['skills'])
    about = f'''<section id="about" class="about-section reveal" aria-labelledby="about-title"><div class="section-heading"><h2 id="about-title">{text(a['about_heading'])}</h2><span>People, places & practical work</span></div><div class="about-grid"><div><p class="about-intro">{text(a['about_intro'])}</p>{about_paragraphs}<a class="resume-link" href="{resume}">Read my résumé</a></div><aside class="education"><p class="note-label">Education</p><p>{text(a['university'])}</p><p class="meta-topic">{text(a['degree'])}<br>{text(a['graduation'])}</p><p class="note-label education-label">Tools I work with</p><p class="meta-topic">{skills}</p></aside></div><div class="experience-list">{experience}</div></section>'''
    contact_links = links([dict(label='Email me',url='mailto:'+email),dict(label='GitHub',url=c['github']),dict(label='Résumé',url=c['resume'])])
    contact = f'''<section id="contact" class="contact-section reveal"><p class="eyebrow">Correspondence</p><h2>{text(c['heading'])}</h2>{paragraphs(c['message'])}{contact_links}</section>'''
    footer = f'<footer><span>{text(a["name"])} <span class="footer-slash">/</span> {text(a["handle"])}</span><span>{text(c["footer_interests"])}</span><a href="#">Back to top</a></footer>'
    values = dict(opening=opening,projects='\n'.join(projects),about=about,contact=contact,footer=footer,resume=resume,brand=text(a['brand']),description=text(a['description']),page_title=text(a['page_title']),css_hash=hashlib.sha256((ROOT/'styles.css').read_bytes()).hexdigest()[:10],js_hash=hashlib.sha256((ROOT/'script.js').read_bytes()).hexdigest()[:10])
    return Template((ROOT/'templates/index.html').read_text()).substitute(values)

def load():
    return {name:json.loads((ROOT/f'content/{name}.json').read_text()) for name in ['about','projects','experience','contact']}

def build():
    html = render(load())
    (ROOT/'index.html').write_text(html)
    out=ROOT/'_site';out.mkdir(exist_ok=True)
    for name in ['index.html','styles.css','script.js','favicon.svg','Jake-Hwang-Resume.pdf']:
        shutil.copy2(ROOT/name,out/name)
    # Only public assets are deployed; source/config and content history remain in GitHub.
    shutil.copytree(ROOT/'admin',out/'admin',dirs_exist_ok=True)
    print('Built public portfolio from editable content.')

if __name__=='__main__': build()
