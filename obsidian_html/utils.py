import regex as re
import os
import markdown2
from obsidian_html import GLOBAL


def slug_case(text):
    text = text.replace(".", "dot")
    text = text.replace("_", "-")
    return re.sub(r'[^\w\-/]+', '-', text).lower()


def md_link(text, link):
    print(text, link)
    if re.search(r".*png$", text) is None:
        result = "[" + text + "](" + link + (".html" if GLOBAL.HTML_LINK_EXTENSIONS else "") + ")"
    else:
        result = "[" + text + "](" + text + ")"
    print(result)
    return result


def extract_links_from_file(document):
    matches = re.finditer(r"\[{2}([^\]]*?)[|#\]]([^\]]*?)\]+", document)

    links = []
    for match in matches:
        link = match.group(1)
        links.append(link)

    return links


def find_backlinks(target_note_name, all_notes):
    backlinks = []
    for note in all_notes:
        links = extract_links_from_file(note["content"])
        if target_note_name in links:
            backlinks.append({"text": note["filename"].replace(".md", ""),
                              "link": slug_case(note["filename"].replace(".md", ""))})

    backlinks = sorted(backlinks, key=lambda x: x['text'])

    return backlinks

def find_tags(document):
    tags = [match.group(1) for match in re.finditer(r"\s#([\p{L}_-]+)", document)]
    # Sort by length (longest first) to fix issues pertaining to tags beginning with the same word.
    tags.sort(key=lambda x: len(x), reverse=True)
    
    return tags

def render_markdown(text):
    # Escaped curly braces lose their escapes when formatted. I'm suspecting
    # this is from markdown2, as I haven't found anyplace which could
    # do this among my own formatter functions. Therefore I double escape them.
    text = text.replace(r"\{", r"\\{").replace(r"\}", r"\\}")

    markdown2_extras = [
        # Parser should work withouth strict linebreaks.
        "break-on-newline",
        # Make slug IDs for each header. Needed for internal header links.
        "header-ids",
        # Support for strikethrough formatting.
        "strike",
        # GFM tables.
        "tables",
        # Support for lists that start without a newline directly above.
        "cuddled-lists",
        # Support Markdown inside html tags
        "markdown-in-html",
        # Disable formatting via the _ character. Necessary for code and TeX
        "code-friendly",
        # Support for Obsidian's footnote syntax
        "footnotes",
        # Enable task list checkboxes - [ ]
        "task_list"
    ]

    return markdown2.markdown(text, extras=markdown2_extras)
