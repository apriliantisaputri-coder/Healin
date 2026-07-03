"""
Patch kompatibilitas untuk library Experta.

Experta ditulis untuk Python < 3.10 dan masih mengacu ke
`collections.Mapping` / `collections.MutableMapping`, padahal sejak
Python 3.10 alias tersebut dipindah ke `collections.abc`.
Fungsi ini WAJIB dipanggil sebelum `import experta` di seluruh proyek
apabila dijalankan pada Python 3.10 ke atas (termasuk Python 3.11/3.12
yang menjadi target proyek Heal.In).
"""
import collections
import collections.abc


def patch_collections_compat() -> None:
    if not hasattr(collections, "Mapping"):
        collections.Mapping = collections.abc.Mapping
    if not hasattr(collections, "MutableMapping"):
        collections.MutableMapping = collections.abc.MutableMapping
    if not hasattr(collections, "Sequence"):
        collections.Sequence = collections.abc.Sequence
