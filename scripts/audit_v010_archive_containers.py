"""Read-only forensic comparison of accepted v0.1.0 archives and actual PyPI archives.

Reports observable container differences. Does not claim reproducible-build equivalence,
approve a release, or modify published artifacts.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import struct
import tarfile
import urllib.error
import urllib.request
import zipfile

REPO = "lonewolf15116/reliable-masked-tabular-imputation"
ARTIFACT_ID = "14486589094"
EXPECTED = {
    "reliable_masked_tabular_imputation-0.1.0-py3-none-any.whl": (
        "1a70b24bac9dd6f0873c7ae690e9edabb792946cc7f0fa8e92e716c6da7c635a",
        "761b17fc38a160ca20d09bf311eef3c9ab18c918982e55c46009515eb3367f48",
    ),
    "reliable_masked_tabular_imputation-0.1.0.tar.gz": (
        "bab9c94375dfb47ed4002d9910e01b9aae53940f9b95c53a9690e3836e693c7c",
        "222775460729549de57a4b3d348784dba4474a3e078010be710493d528ce3d66",
    ),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def retrieve(url: str, headers: dict[str, str] | None = None) -> bytes:
    request = urllib.request.Request(
        url, headers={"User-Agent": "rmti-v010-container-audit/1.0", **(headers or {})}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def accepted_zip() -> bytes:
    token = os.environ["GH_TOKEN"]
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/actions/artifacts/{ARTIFACT_ID}/zip",
        headers={
            "User-Agent": "rmti-v010-container-audit/1.0",
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
        },
    )

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, hdrs, newurl):
            return None

    try:
        urllib.request.build_opener(NoRedirect).open(request, timeout=30)
    except urllib.error.HTTPError as exc:
        if exc.code not in (301, 302, 303, 307, 308):
            raise
        signed = exc.headers.get("Location")
        if not signed or not signed.startswith("https://"):
            raise RuntimeError("GitHub did not return an HTTPS artifact location")
        return retrieve(signed)
    raise RuntimeError("Expected a signed artifact redirect from GitHub")


def first_difference(a: bytes, b: bytes) -> int | None:
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return min(len(a), len(b)) if len(a) != len(b) else None


def zip_details(data: bytes) -> dict:
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if archive.testzip() is not None:
            raise ValueError("Invalid CRC in wheel")
        entries = {}
        order = []
        for info in archive.infolist():
            if info.is_dir():
                continue
            order.append(info.filename)
            entries[info.filename] = {
                "sha256": sha(archive.read(info.filename)),
                "size": info.file_size,
                "compressed_size": info.compress_size,
                "compression": info.compress_type,
                "date_time": list(info.date_time),
                "crc32": info.CRC,
                "flags": info.flag_bits,
                "extra_hex": info.extra.hex(),
                "comment_hex": info.comment.hex(),
                "external_attr": info.external_attr,
                "create_system": info.create_system,
                "header_offset": info.header_offset,
            }
        return {"order": order, "entries": entries, "zip_comment_hex": archive.comment.hex()}


def gzip_header(data: bytes) -> dict:
    if data[:2] != b"\x1f\x8b":
        raise ValueError("Not a gzip stream")
    return {
        "compression_method": data[2],
        "flags": data[3],
        "mtime": struct.unpack("<I", data[4:8])[0],
        "xfl": data[8],
        "os": data[9],
        "first_10_bytes_hex": data[:10].hex(),
    }


def tar_details(data: bytes) -> dict:
    plain = gzip.decompress(data)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        order = []
        entries = {}
        for info in archive.getmembers():
            name = info.name
            order.append(name)
            payload_hash = sha(archive.extractfile(info).read()) if info.isfile() else None
            entries[name] = {
                "type": str(info.type),
                "size": info.size,
                "mtime": info.mtime,
                "mode": info.mode,
                "uid": info.uid,
                "gid": info.gid,
                "uname": info.uname,
                "gname": info.gname,
                "linkname": info.linkname,
                "pax_headers": info.pax_headers,
                "payload_sha256": payload_hash,
            }
    return {
        "gzip_header": gzip_header(data),
        "uncompressed_tar_sha256": sha(plain),
        "uncompressed_tar_size": len(plain),
        "order": order,
        "entries": entries,
    }


def compare(accepted: bytes, published: bytes, filename: str) -> dict:
    a_sha, p_sha = EXPECTED[filename]
    if sha(accepted) != a_sha or sha(published) != p_sha:
        raise AssertionError("Observed SHA differs from independent historical evidence")
    a = zip_details(accepted) if filename.endswith(".whl") else tar_details(accepted)
    b = zip_details(published) if filename.endswith(".whl") else tar_details(published)
    aa, bb = a["entries"], b["entries"]
    removed = sorted(aa.keys() - bb.keys())
    added = sorted(bb.keys() - aa.keys())
    differences = {}
    for name in sorted(aa.keys() & bb.keys()):
        fields = sorted(set(aa[name]) | set(bb[name]))
        changed = {field: {"accepted": aa[name].get(field), "published": bb[name].get(field)}
                   for field in fields if aa[name].get(field) != bb[name].get(field)}
        if changed:
            differences[name] = changed
    result = {
        "filename": filename,
        "accepted_binary_sha256": a_sha,
        "published_binary_sha256": p_sha,
        "same_binary": accepted == published,
        "accepted_bytes": len(accepted),
        "published_bytes": len(published),
        "first_binary_difference_offset": first_difference(accepted, published),
        "only_accepted": removed,
        "only_pypi": added,
        "entry_order_equal": a["order"] == b["order"],
        "entry_metadata_differences": differences,
        "extracted_file_contents_equal": not removed and not added and
            all(aa[n]["sha256"] == bb[n]["sha256"] for n in aa if filename.endswith(".whl")) if filename.endswith(".whl")
            else (not removed and not added and all(
                aa[n]["payload_sha256"] == bb[n]["payload_sha256"] for n in aa)),
    }
    if filename.endswith(".whl"):
        result["zip_comment_equal"] = a["zip_comment_hex"] == b["zip_comment_hex"]
    else:
        result["gzip_header_accepted"] = a["gzip_header"]
        result["gzip_header_pypi"] = b["gzip_header"]
        result["uncompressed_tar_equal"] = (
            a["uncompressed_tar_sha256"] == b["uncompressed_tar_sha256"]
        )
        result["uncompressed_tar_sha256_accepted"] = a["uncompressed_tar_sha256"]
        result["uncompressed_tar_sha256_pypi"] = b["uncompressed_tar_sha256"]
    return result


def main() -> None:
    archive = accepted_zip()
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        originals = {name: bundle.read(name) for name in bundle.namelist() if not name.endswith("/")}
    pypi = json.loads(retrieve("https://pypi.org/pypi/reliable-masked-tabular-imputation/0.1.0/json"))
    published = {x["filename"]: x for x in pypi["urls"]}
    report = {}
    for filename in EXPECTED:
        matching = [blob for name, blob in originals.items() if name.endswith(filename)]
        if len(matching) != 1:
            raise AssertionError(f"Expected one accepted artifact for {filename}: {len(matching)}")
        data = retrieve(published[filename]["url"])
        if sha(data) != published[filename]["digests"]["sha256"]:
            raise AssertionError("PyPI supplied digest does not match downloaded bytes")
        result = compare(matching[0], data, filename)
        report[filename] = result
        print("FILE", filename, flush=True)
        print("EXTRACTED_CONTENT_EQUAL", result["extracted_file_contents_equal"], flush=True)
        print("ENTRY_ORDER_EQUAL", result["entry_order_equal"], flush=True)
        print("METADATA_DIFFERENCES", json.dumps(result["entry_metadata_differences"], sort_keys=True), flush=True)
        if filename.endswith(".tar.gz"):
            print("UNCOMPRESSED_TAR_EQUAL", result["uncompressed_tar_equal"], flush=True)
            print("GZIP_HEADERS", json.dumps({"accepted": result["gzip_header_accepted"], "pypi": result["gzip_header_pypi"]}), flush=True)
        else:
            print("ZIP_COMMENT_EQUAL", result["zip_comment_equal"], flush=True)
        print("FIRST_BINARY_DIFFERENCE_OFFSET", result["first_binary_difference_offset"], flush=True)
    Path("archive_container_diagnosis.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
