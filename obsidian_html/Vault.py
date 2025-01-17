import os
import regex as re
import shutil
from obsidian_html.utils import slug_case, md_link, render_markdown
from obsidian_html.Note import Note


class Vault:
    def __init__(self, vault_root, extra_folders=[], html_template=None, filter=[]):
        self.vault_root = vault_root
        self.filter = filter
        self.notes = self._find_files(vault_root, extra_folders)
        self.media = self._find_media_files(vault_root, extra_folders)
        self.extra_folders = extra_folders
        self._add_backlinks()

        self.html_template = html_template
        if html_template:
            with open(html_template, "r", encoding="utf8") as f:
                self.html_template = f.read()

    def _add_backlinks(self):
        for i, note in enumerate(self.notes):
            # Make temporary list of all notes except current note in loop
            others = [other for other in self.notes if other != note]
            backlinks = self.notes[i].find_backlinks(others)
            if backlinks:
                self.notes[i].backlinks += "\n<div class=\"backlinks\" markdown=\"1\">\n"
                for backlink in backlinks:
                    self.notes[i].backlinks += f"- {backlink.md_link()}\n"
                self.notes[i].backlinks += "</div>"

                self.notes[i].backlinks = render_markdown(self.notes[i].backlinks)

    def export_html(self, out_dir):
        # Ensure out_dir exists, as well as its sub-folders.
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        for folder in self.extra_folders:
            if not os.path.exists(os.path.join(out_dir, folder)):
                os.makedirs(os.path.join(out_dir, folder))

        for note in self.notes:
            if self.html_template:
                html = self.html_template.format(title=note.title, content=note.html(), backlinks=note.backlinks)
            else:
                html = note.html()
            with open(os.path.join(out_dir, note.filename_html), "w", encoding="utf8") as f:
                f.write(html)

    def copy_media(self, out_dir):
        # Ensure out_dir exists, as well as its sub-folders.
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        for folder in self.extra_folders:
            if not os.path.exists(os.path.join(out_dir, folder)):
                os.makedirs(os.path.join(out_dir, folder))

        for media in self.media:
            print(f'copying {media}')
            shutil.copy2(media, out_dir)  # target filename is /dst/dir/file.ext

    def _find_files(self, vault_root, extra_folders):
        # Find all markdown-files in vault root.
        md_files = self._find_md_files(vault_root)

        # extra_folders = [x[0] for x in os.walk(vault_root)]
        # Find all markdown-files in each extra folder.
        for folder in extra_folders:
            md_files += self._find_md_files(os.path.join(vault_root, folder), is_extra_dir=True)

        return md_files

    def _find_media_files(self, vault_root, extra_folders):
        # Find all media-files in vault root.
        media_files = self._find_image_files(vault_root)

        # Find all media-files in each extra folder.
        for folder in extra_folders:
            media_files += self._find_image_files(os.path.join(vault_root, folder), is_extra_dir=True)

        return media_files

    def _find_md_files(self, root, is_extra_dir=False):
        md_files = []
        for md_file in os.listdir(root):
            # Check if the element in 'root' has the extension .md and is indeeed a file
            if not (md_file.endswith(".md") and os.path.isfile(os.path.join(root, md_file))):
                continue
            
            note = Note(os.path.join(root, md_file), is_extra_dir=is_extra_dir)
            
            # Filter tags
            if self.filter:
                for tag in self.filter:
                    if tag in note.tags:
                        md_files.append(note)
                        break
            else:
                md_files.append(note)

        return md_files

    def _find_image_files(self, root, is_extra_dir=False):
        image_files = []
        for image_file in os.listdir(root):
            # Check if the element in 'root' has a media extension and is indeed a file indeed
            if image_file.lower().endswith(('.png', '.jpg', '.jpeg')) and os.path.isfile(os.path.join(root, image_file)):
                print(f'mediafile : {image_file}')
                image_files.append(os.path.join(root, image_file))

        return image_files