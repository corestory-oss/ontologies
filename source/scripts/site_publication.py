# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Static publication identity; canonical URLs describe intent, not deployment."""
from html import escape
import json
import os
from pathlib import Path, PurePosixPath
import shutil
from urllib.parse import quote

SITE_ORIGIN = "https://ontologies.corestory.ai"
SITE_NAME = "CoreStory Ontologies"
SOCIAL_IMAGE = "assets/ontology-social.png"
SOCIAL_ALT = "CoreStory Ontologies reference library: SAO software structures and SpecSpec specification and evidence."
SOURCE_MANIFEST = "web/public-source-manifest.json"
# These roots bound drift detection, never authorize recursive publication.
SOURCE_REVIEW_ROOTS = ("ontologies", "scripts", "tests", "examples", "legacy", "docs", "dist")


def regular_source_file(root, relative):
    """Reject file and ancestor symlinks before opening any source bytes."""
    root = Path(root)
    path = root
    if path.is_symlink():
        raise ValueError(f"Symlink in public source: {root}")
    for part in PurePosixPath(relative).parts:
        path /= part
        if path.is_symlink():
            raise ValueError(f"Symlink in public source: {relative}")
    if not path.is_file():
        raise ValueError(f"Missing regular public source file: {relative}")
    return path


def source_manifest(root):
    """An exact reviewed inventory is the authority, not the directory contents."""
    path = regular_source_file(root, SOURCE_MANIFEST)
    manifest = json.loads(path.read_text())
    files, excluded = manifest.get("files"), manifest.get("excluded")
    if manifest.get("version") != 1 or not isinstance(files, list) or not isinstance(excluded, dict):
        raise ValueError("Invalid public source manifest version or inventory")
    if not all(isinstance(name, str) for name in files) or files != sorted(set(files)):
        raise ValueError("Public source manifest files must be sorted and unique")
    if set(files) & set(excluded):
        raise ValueError("Public source manifest includes an explicitly excluded file")
    for name in [*files, *excluded]:
        parts = PurePosixPath(name).parts
        if (not parts or name != PurePosixPath(name).as_posix() or name.startswith("/")
                or any(part in (".", "..") for part in parts)
                or any(character in name for character in "\\\\:*?[]#%")
                or PurePosixPath(name).name == "index.html"):
            raise ValueError(f"Invalid public source manifest path: {name}")
    if not {"LICENSE", "NOTICE"}.issubset(files):
        raise ValueError("Public source manifest must retain LICENSE and NOTICE")
    return manifest


def source_indexes(files):
    """Only the ancestors of reviewed files receive generated directory indexes."""
    directories = {PurePosixPath(".")}
    for name in files:
        directories.update(PurePosixPath(name).parents)
    return {str(directory / "index.html") for directory in directories}


def validate_source_inputs(root, manifest):
    """Refuse unreviewed nested files; never follow symlinks, even excluded ones."""
    root = Path(root)
    allowed = set(manifest["files"]) | set(manifest["excluded"])
    for name in manifest["files"]:
        regular_source_file(root, name)
    for scope in SOURCE_REVIEW_ROOTS:
        start = root / scope
        if start.is_symlink():
            raise ValueError(f"Symlink in public source: {scope}")
        for directory, folders, files in os.walk(start, followlinks=False):
            for name in folders + files:
                path = Path(directory) / name
                relative = path.relative_to(root).as_posix()
                if path.is_symlink():
                    raise ValueError(f"Symlink in public source: {relative}")
                if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc" and relative not in allowed:
                    raise ValueError(f"Unreviewed public source input: {relative}")
                if not path.is_file() and not path.is_dir():
                    raise ValueError(f"Nonregular public source input: {relative}")


def copy_public_sources(root, destination, manifest):
    """Copy only explicit files after checking the entire source selection."""
    validate_source_inputs(root, manifest)
    destination = Path(destination)
    if destination.is_symlink() or destination.exists():
        raise ValueError(f"Public source destination must not exist: {destination}")
    for name in manifest["files"]:
        path = regular_source_file(root, name)
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target, follow_symlinks=False)


def check_public_sources(root, directory, failures):
    """Check every nested payload path and byte, not merely the source root."""
    manifest = source_manifest(root)
    source = Path(directory) / "source"
    if source.is_symlink() or not source.is_dir():
        failures.append("Missing regular public source directory or symlink: source")
        return
    actual = set()
    expected = set(manifest["files"]) | source_indexes(manifest["files"])
    expected_dirs = {str(PurePosixPath(name).parent) for name in source_indexes(manifest["files"])}
    for folder, dirs, files in os.walk(source, followlinks=False):
        for name in dirs + files:
            path = Path(folder) / name
            relative = path.relative_to(source).as_posix()
            if path.is_symlink():
                failures.append("Symlink in public source output: " + relative)
            elif path.is_dir():
                if relative not in expected_dirs:
                    failures.append("Unexpected public source directory: " + relative)
            elif path.is_file():
                actual.add(relative)
            else:
                failures.append("Nonregular public source output: " + relative)
    for name in sorted(actual - expected):
        failures.append("Unexpected public source file: " + name)
    for name in sorted(expected - actual):
        failures.append("Missing public source file: " + name)
    for name in manifest["files"]:
        if name in actual and (source / name).read_bytes() != regular_source_file(root, name).read_bytes():
            label = "Missing or changed source attribution: " if name in ("LICENSE", "NOTICE") else "Changed public source bytes: "
            failures.append(label + name)
    published = Path(directory) / "source-manifest.json"
    if published.is_symlink() or not published.is_file() or published.read_bytes() != regular_source_file(root, SOURCE_MANIFEST).read_bytes():
        failures.append("Public source inventory differs from the reviewed manifest")


def canonical_url(target):
    """Directory indexes have one canonical URL; runtime links stay relative."""
    path = Path(target).as_posix()
    if path == "index.html":
        path = ""
    elif path.endswith("/index.html"):
        path = path[:-len("index.html")]
    return SITE_ORIGIN + "/" + quote(path, safe="/")


def publication_head(title, description, target, *, noindex=False):
    """Use the same escaped identity in search, Open Graph and Twitter cards."""
    url = canonical_url(target)
    image = SITE_ORIGIN + "/" + SOCIAL_IMAGE
    fields = [("name", "description", description),
              ("property", "og:type", "website"),
              ("property", "og:site_name", SITE_NAME),
              ("property", "og:title", title),
              ("property", "og:description", description),
              ("property", "og:url", url),
              ("property", "og:image", image),
              ("property", "og:image:type", "image/png"),
              ("property", "og:image:width", "1200"),
              ("property", "og:image:height", "630"),
              ("property", "og:image:alt", SOCIAL_ALT),
              ("name", "twitter:card", "summary_large_image"),
              ("name", "twitter:title", title),
              ("name", "twitter:description", description),
              ("name", "twitter:image", image),
              ("name", "twitter:image:alt", SOCIAL_ALT)]
    if noindex:
        fields.append(("name", "robots", "noindex, follow"))
    return (f'<link rel="canonical" href="{escape(url, quote=True)}">\n'
            + "\n".join(f'<meta {attribute}="{key}" content="{escape(value, quote=True)}">'
                        for attribute, key, value in fields))


def write_crawl_files(output):
    """List built HTML only; exclude the error response from indexing."""
    output = Path(output)
    urls = [canonical_url(path.relative_to(output)) for path in sorted(output.rglob("*.html"))
            if path != output / "404.html"]
    (output / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{escape(url)}</loc></url>\n" for url in sorted(urls))
        + '</urlset>\n')
    (output / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: " + SITE_ORIGIN + "/sitemap.xml\n")
    (output / "healthz").write_text("ok\n")
