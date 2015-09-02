import re

from sectiondoc.sections import (
    attributes, methods_table, notes_paragraph, item_list, arguments)
from sectiondoc.renderers import Attribute, Method, Argument, ListItem
from sectiondoc.items import Item, MethodItem
from sectiondoc.items.regex import header_regex
from sectiondoc.styles.doc_render import DocRender
from sectiondoc.styles.style import Style
from sectiondoc.util import add_indent, trim_indent


definition_regex = re.compile(r"""
\*{0,2}            #  no, one or two stars
\w+\s:             #  a word followed by a space and a semicolumn
(.+)?              #  a definition
$                  # match at the end of the line
""", re.VERBOSE)


class PlainDefinition(Item):
    """ A Definition parser that treats anything after the ``:`` as a single
    classifier

    The expected format is::

    +-------------------------------------------------+
    | term [ " : " classifier ]                       |
    +-------------------------------------------------+

    """

    @classmethod
    def is_item(cls, line):
        return definition_regex.match(line) is not None

    @classmethod
    def parse(cls, lines):
        header = lines[0].strip()
        term, classifier = header_regex.split(header, maxsplit=1) if \
            (' :' in header) else (header, '')
        trimed_lines = trim_indent(lines[1:]) if (len(lines) > 1) else ['']
        definition = [line.rstrip() for line in trimed_lines]
        return cls(term.strip(), [classifier.strip()], definition)


def example_paragraph(doc, header, renderer=None, item_class=None):
    """ Render the example section to use the ``::`` directive.

    The section is expected to be given as a paragraph.

    """
    paragraph = doc.get_next_paragraph()
    lines = ['**{0}**'.format(header), '::', '']
    lines += add_indent(paragraph)
    return lines


def returns_section(doc, header, renderer=None, item_class=None):
    """ A return item list section that also accepts a paragraph as
    a description.

    """
    lines = item_list(doc, header, renderer, item_class)
    if len(lines) == 1:
        paragraph = doc.get_next_paragraph()
        lines += add_indent(paragraph)
    return lines


def class_section(lines):
    return DocRender(
        lines,
        sections={
            'Attributes': (attributes, Attribute, PlainDefinition),
            'Arguments': (arguments, Argument, PlainDefinition),
            'Parameters': (arguments, Argument, PlainDefinition),
            'Methods': (methods_table, Method, MethodItem),
            'Note': (notes_paragraph, None, None),
            'Notes': (notes_paragraph, None, None),
            'Example': (example_paragraph, None, None),
            'Examples': (example_paragraph, None, None)})


def function_section(lines):
    return DocRender(
        lines,
        sections={
            'Returns': (returns_section, ListItem, PlainDefinition),
            'Arguments': (arguments, Argument, PlainDefinition),
            'Parameters': (arguments, Argument, PlainDefinition),
            'Raises': (returns_section, ListItem, PlainDefinition),
            'Yields': (item_list, ListItem, PlainDefinition),
            'Note': (notes_paragraph, None, None),
            'Notes': (notes_paragraph, None, None),
            'Example': (example_paragraph, None, None),
            'Examples': (example_paragraph, None, None)})


def setup(app):
    """ Traits custom sectiondoc Style """
    style = Style({
        'class': class_section,
        'function': function_section,
        'method': function_section})
    app.setup_extension('sphinx.ext.autodoc')
    app.connect('autodoc-process-docstring', style.render_docstring)
