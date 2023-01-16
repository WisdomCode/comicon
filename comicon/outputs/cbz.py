import zipfile
from pathlib import Path

from lxml import etree
from lxml.builder import E

from .. import cirtools


def create_comic(cir_path: Path, dest: Path) -> None:
    """
    Create a comic from the given IR path.

    :param `cir_path`: The path to the IR folder.
    :param `dest`: The path to the destination file.
    """
    comic = cirtools.read_metadata(cir_path)

    tree = E.ComicInfo(
        E.Title(
            comic.metadata.title,
        ),
        E.Summary(comic.metadata.description),
        E.Writer(", ".join(comic.metadata.authors)),
        E.Genre(", ".join(comic.metadata.genres)),
        # TODO: add pages
    )
    text_xml = etree.tostring(
        tree, pretty_print=True, encoding="utf-8", xml_declaration=True
    ).decode()

    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as file:
        for i, chap in enumerate(comic.chapters):
            chap_path = cir_path / chap.slug
            rel_chap_path = chap_path.with_name(f"{i:05}-{chap.slug}")
            for image in sorted(chap_path.iterdir()):
                new_img_path = rel_chap_path / image.name
                file.write(
                    image,
                    new_img_path.absolute().relative_to(cir_path),
                    zipfile.ZIP_DEFLATED,
                )

        if comic.metadata.cover_path_rel:
            cover_path = cir_path / comic.metadata.cover_path_rel
            file.write(
                cover_path,
                # rename cover to appear first in the archive
                cover_path.with_stem("__cover").absolute().relative_to(cir_path),
                zipfile.ZIP_DEFLATED,
            )
        file.writestr("ComicInfo.xml", text_xml)
        file.writestr("data.json", comic.to_json())
