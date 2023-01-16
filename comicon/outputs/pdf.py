from pathlib import Path

from PIL import Image

from .. import cirtools

PDF_IMAGE_MAX_INTERVAL = 200  # adjust for memory as necessary
PDF_IMAGE_MIN_INTERVAL_FACTOR = 0.12


def create_comic(cir_path: Path, dest: Path) -> None:
    comic = cirtools.read_metadata(cir_path)

    # TODO: consider using a generator instead of a list
    images: list[Image.Image] = []
    if comic.metadata.cover_path_rel:
        images.append(Image.open(cir_path / comic.metadata.cover_path_rel))

    for chap in comic.chapters:
        images.extend(Image.open(f) for f in sorted((cir_path / chap.slug).iterdir()))

    # interval for num pdf images to process
    # at one time
    interval = round(
        min(
            PDF_IMAGE_MAX_INTERVAL,
            max(1, len(images) * PDF_IMAGE_MIN_INTERVAL_FACTOR),
        )
    )

    for i in range(0, len(images), interval):
        append_images = images[i + 1 : i + interval] if len(images) > i + 1 else []
        author = ", ".join(comic.metadata.authors)

        images[i].save(
            dest,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=append_images,
            title=comic.metadata.title,
            author=author,
            append=i != 0,
            creator=comic.to_json(),
            producer="comicon",
            keywords=", ".join(comic.metadata.genres),
            subject=comic.metadata.description,
        )

        for j in images[i : i + interval]:
            j.close()
