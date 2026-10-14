import pytest
from PyQt6.QtGui import QPixmap
from app.threads import ThumbnailCache


def test_thumbnail_cache_lru_eviction(qtbot):
    cache = ThumbnailCache(max_size=3)

    pix1 = QPixmap(10, 10)
    pix2 = QPixmap(10, 10)
    pix3 = QPixmap(10, 10)
    pix4 = QPixmap(10, 10)

    cache.set("url1", pix1)
    cache.set("url2", pix2)
    cache.set("url3", pix3)

    assert cache.get("url1") is pix1
    assert cache.get("url2") is pix2
    assert cache.get("url3") is pix3

    # Access url1 so url2 becomes the oldest unused
    _ = cache.get("url1")

    # Insert url4 -> url2 should be evicted!
    cache.set("url4", pix4)

    assert cache.get("url1") is pix1
    assert cache.get("url2") is None  # evicted!
    assert cache.get("url3") is pix3
    assert cache.get("url4") is pix4


def test_thumbnail_cache_update_existing(qtbot):
    cache = ThumbnailCache(max_size=2)
    pix1 = QPixmap(10, 10)
    pix1_new = QPixmap(20, 20)
    pix2 = QPixmap(10, 10)

    cache.set("url1", pix1)
    cache.set("url2", pix2)
    # Update url1 with new pixmap
    cache.set("url1", pix1_new)

    assert cache.get("url1") is pix1_new
    assert cache.get("url2") is pix2


def test_thumbnail_cache_clear(qtbot):
    cache = ThumbnailCache(max_size=5)
    cache.set("url1", QPixmap(5, 5))
    cache.set("url2", QPixmap(5, 5))
    assert cache.get("url1") is not None
    cache.clear()
    assert cache.get("url1") is None
    assert cache.get("url2") is None
