"""Custom docutils / Sphinx directives specific to nengo.github.io."""

from datetime import datetime
import errno
import os

from docutils import nodes
from docutils.parsers.rst import Directive, directives


class Project(Directive):
    """The Project directive is used to describe Nengo projects.

    It attempts to give an attractive and uniform appearance to
    each project listing with minimal effort for authors.
    """

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        "repo": directives.unchanged_required,
        "maintainer": directives.unchanged_required,
        "contact": directives.unchanged,
        "pypi": directives.unchanged,
        "docs": directives.unchanged,
    }
    has_content = True

    @staticmethod
    def linked_image(img, href, **image_args):
        a = nodes.reference(refuri=href)
        a += nodes.image(uri=img, **image_args)
        return a

    def run(self):
        self.assert_has_content()

        # Get info from directive
        name = self.arguments[0].strip()
        org, repo = self.options["repo"].strip().split("/")
        maintainer = self.options["maintainer"]
        contact = self.options.get("contact", None)
        pypi = self.options.get("pypi", None)
        docs = self.options.get("docs", None)

        # Parent container holds info and description
        parent = nodes.container()
        parent["classes"].append("project")
        self.add_name(parent)

        # Make a container for meta-info about the project
        info = nodes.container()
        info["classes"].append("project-info")
        # Title contains name, linked to docs if available
        title = nodes.strong(self.block_text, name)
        if docs is not None:
            title = nodes.strong(self.block_text)
            title += nodes.reference(refuri=docs, text=name)
        info += title

        shields = "https://img.shields.io"
        # Badges contains links to Github, PyPI, etc
        badges = nodes.paragraph(self.block_text)
        badges["classes"].append("project-badges")

        if docs is not None:
            badges += self.linked_image(
                img="%s/badge/documentation--green.svg?style=social" % shields,
                href=docs)

        badges += self.linked_image(
            img="%s/github/stars/%s/%s.svg?style=social&label=Github" % (
                shields, org, repo),
            href="https://github.com/%s/%s" % (org, repo))

        if pypi is not None:
            badges += self.linked_image(
                img="%s/pypi/v/%s.svg" % (shields, pypi),
                href="https://pypi.python.org/pypi/%s" % (pypi,))
        info += badges

        # List maintainer
        maint = nodes.paragraph(self.block_text)
        maint["classes"].append("project-maintainer")

        maint += nodes.inline(self.block_text, "Maintainer: ")
        if org == "nengo":
            maint += self.linked_image(
                img="https://www.nengo.ai/design/_images/small-light.svg",
                href="https://github.com/nengo",
                alt="Managed by Nengo team",
                height="16px")
        if contact is not None:
            contact_node = nodes.reference(refuri="mailto:%s" % contact)
            maint += contact_node
        else:
            contact_node = maint
        contact_node += nodes.inline(self.block_text, maintainer)
        info += maint

        # Make a container for the description
        description = nodes.container()
        description["classes"].append("project-description")
        self.state.nested_parse(self.content, self.content_offset, description)

        # Add to parent container
        parent += info
        parent += description
        return [parent]


class Model(Directive):
    """The Model directive is used to describe Nengo models.

    It attempts to give an attractive and uniform appearance to
    each project listing with minimal effort for authors.
    """

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        "code": directives.unchanged_required,
        "month": directives.unchanged,
        "year": directives.unchanged_required,
        "authors": directives.unchanged_required,
        "keywords": directives.unchanged_required,
        "pub": directives.unchanged,
        "pub-link": directives.unchanged,
        "requires": directives.unchanged,
    }
    has_content = True

    def run(self):
        self.assert_has_content()

        # Get info from directive
        name = self.arguments[0].strip()
        code = self.options["code"]
        month = self.options.get("month", None)
        year = self.options["year"]
        authors = self.options["authors"]
        keywords = [k.strip()
                    for k in self.options["keywords"].split(",")
                    if len(k.strip()) > 0]
        pub = self.options.get("pub", None)
        publink = self.options.get("pub-link", None)
        requires = [r.strip()
                    for r in self.options.get("requires", "").split(",")
                    if len(r.strip()) > 0]

        # Parent container holds info and description
        parent = nodes.container()
        parent["classes"].append("model")
        self.add_name(parent)

        # Make a container for info about the model
        info = nodes.container()
        info["classes"].append("model-info")
        title = nodes.container()
        title["classes"].append("model-header")
        tlink = nodes.reference(refuri=code, text=name)
        tlink["classes"].append("model-title")
        title += nodes.strong(self.block_text, "", tlink)
        for requirement in requires:
            title += nodes.emphasis(self.block_text, requirement)
        info += title

        byline = nodes.paragraph()
        byline["classes"].append("model-byline")
        n = nodes.inline(self.block_text, authors)
        n["classes"].append("model-authors")
        byline += n
        byline += nodes.inline(self.block_text, " (")
        datestr = year
        if month is not None:
            try:
                monthstr = datetime.strptime(month, "%B").strftime("%b")
            except ValueError:
                monthstr = datetime.strptime(month, "%b").strftime("%b")
            datestr = "%s, %s" % (monthstr, year)
        d = nodes.inline(self.block_text, datestr)
        d["classes"].append("model-date")
        byline += d
        byline += nodes.inline(self.block_text, ")")
        info += byline

        # Render the publication, if there is one
        if pub is not None or publink is not None:
            pubnode = nodes.paragraph()
            pubnode["classes"].append("model-pub")
            if pub is not None:
                pubnode += nodes.inline(self.block_text, "Published in ")
                pubtext = pub
            else:
                pubtext = "Published"
            if publink is not None:
                pubnode += nodes.reference(refuri=publink, text=pubtext)
            else:
                pubnode += nodes.inline(self.block_text, pubtext)
            info += pubnode

        keynode = nodes.paragraph()
        keynode["classes"].append("model-keywords")
        for keyword in keywords:
            keynode += nodes.emphasis(self.block_text, keyword)
        info += keynode

        # Make a container for details
        details = nodes.container()
        details["classes"].append("model-details")
        self.state.nested_parse(self.content, self.content_offset, details)
        avail = nodes.paragraph(self.block_text)
        avail += nodes.inline(self.block_text, "Code available at ")
        avail += nodes.reference(refuri=code, text=code)
        details += avail

        # Add to parent container
        parent += info
        parent += details

        return [parent]


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def redirect_pages(app, docname):
    redirects = app.config.redirects
    if app.builder.name == 'html':
        for src, dst in redirects:
            fpath = os.path.join(app.outdir, src)
            mkdir_p(os.path.dirname(fpath))
            with open(fpath, "w") as fp:
                fp.write("\n".join([
                    '<!DOCTYPE html>',
                    '<html>',
                    ' <head><title>This page has moved</title></head>',
                    ' <body>',
                    '  <script type="text/javascript">',
                    '   window.location.replace("{0}");',
                    '  </script>',
                    '  <noscript>',
                    '   <meta http-equiv="refresh" content="0; url={0}">',
                    '  </noscript>',
                    ' </body>',
                    '</html>',
                ]).format(dst))


def setup(app):
    # For Project
    app.add_directive("project", Project)

    # For Model
    app.add_directive("model", Model)

    # For redirects
    app.add_config_value("redirects", [], "")
    app.connect("build-finished", redirect_pages)

    return {"version": "0.2.0"}
