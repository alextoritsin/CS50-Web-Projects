import re
from typing import Match

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None


def parse_md(entry):
    """
    Converts Markdown to html. Accepts markdown as an
    agrument, returns html page text.
    """
    title = "none"
    
    # bold replacement func
    def bold_text(m: Match):
        return f"<b>{m.group('bld')}</b>"

    bold_patrn = re.compile(r'(([*_]{2})(?P<bld>.+?)([*_]{2}))')

    # link replacement func
    def link(m: Match):
        name = m.group(4)
        return f"<a href='/wiki/{name}'>{m.group('rt')}</a>"

    link_patrn = re.compile(
        r'(?P<link>\[(?P<rt>(<b>)?(.+)(</b>)?)\]\(/wiki/\4\))')

    # replace bold text and links
    entry = bold_patrn.sub(bold_text, entry)
    entry = link_patrn.sub(link, entry)

    def head_ul(m: Match):
        """
        Search and replace <h> and <ul> tags
        """
        if m.group('hd'):
            nonlocal title
            if title == "none":
                title = m.group('ttl')
            num = len(m.group('nmb'))
            return f"<h{num}>{m.group('ttl')}</h{num}>"

        elif m.group('ul'):
            li_elmts = m.group(0)
            pattern = re.compile(r'\*\s(.+)')
            ul = pattern.sub(li_repl, li_elmts)
            return f"<ul>\n{ul.rstrip()}\n</ul>\r\n"

    def li_repl(m_ul: Match):
        """Search and replace <ul> tag"""
        return f"<li>{m_ul.group(1).rstrip()}</li>"

    head_ul_patrn = re.compile(r"""
    (?P<hd>(?P<nmb>[#]+)\s(?P<ttl>[^\t\n\r\f\v]+))  |   # compile headings pattern
    (?P<ul>(\*\s.+\n?)+)                                 # compile ul pattern                     
    """, re.X)

    before_parag = head_ul_patrn.sub(head_ul, entry)
    splits = re.split(r'\r\n\r\n', before_parag)

    # paragraph replacement
    def parag_repl(m: Match):
        """Replace <p> tag"""
        return f"<p>{m.group(1)}</p>"

    p = re.compile(r'(^[^(<ul)(<h)].+)')
    list_elem = [p.sub(parag_repl, item.strip()) for item in splits if item]
    html = "\n".join(list_elem)
    return title, html
