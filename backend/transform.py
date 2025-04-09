
# backend/transform.py

import xml.etree.ElementTree as ET
import json


def transform(data, fmt="Simdis XML", overrides=None, use_custom_template=False, custom_template=""):
    """
    :param data: Raw XML string
    :param fmt: One of "Simdis XML", "CoT XML", "JSON", "Raw XML"
    :param overrides: Optional dict with keys 'uid', 'lat', 'lon', 'alt'
    :param use_custom_template: If True, use the custom_template string
    :param custom_template: A string containing the template with placeholders
    :return: Transformed string
    """
    try:
        root = ET.fromstring(data.strip())

        if use_custom_template and custom_template:
            try:
                uid = overrides.get("uid") if overrides else root.attrib.get("uid", "UNKNOWN")
                point = root.find("point")
                lat = overrides.get("lat") if overrides else point.attrib.get("lat", "0")
                lon = overrides.get("lon") if overrides else point.attrib.get("lon", "0")
                alt = overrides.get("alt") if overrides else point.attrib.get("hae", "0")
                timestamp = root.attrib.get("time", "UNKNOWN")

                return custom_template.format(uid=uid, lat=lat, lon=lon, alt=alt, timestamp=timestamp)
            except Exception as e:
                return f"[Template Error] {e}"

        if fmt == "Raw XML":
            return data

        elif fmt == "Simdis XML":
            return to_simdis(root, overrides)

        elif fmt == "CoT XML":
            return to_cot(root, overrides)

        elif fmt == "JSON":
            return to_json(root, overrides)

        else:
            raise ValueError("Unsupported format")

    except Exception as e:
        raise ValueError(f"Transform error: {e}")


def to_simdis(root, overrides=None):
    if root.tag == "simdis":
        return ET.tostring(root, encoding="unicode")

    if root.tag != "event":
        raise ValueError("Expected <event> root element")

    uid = overrides.get("uid") if overrides else root.attrib.get("uid")
    timestamp = root.attrib.get("time")
    point = root.find("point")

    if not (uid and timestamp and point is not None):
        raise ValueError("Missing UID, timestamp or point element")

    lat = overrides.get("lat") if overrides else point.attrib.get("lat")
    lon = overrides.get("lon") if overrides else point.attrib.get("lon")
    alt = overrides.get("alt") if overrides else point.attrib.get("hae")

    if None in (lat, lon, alt):
        raise ValueError("Missing lat/lon/alt")

    return (
        f"<simdis>"
        f'  <platform id="{uid}" lat="{lat}" lon="{lon}" alt="{alt}" time="{timestamp}"/>'
        f"</simdis>"
    )


def to_cot(root, overrides=None):
    if root.tag != "event":
        raise ValueError("Expected <event> root element")

    uid = overrides.get("uid") if overrides else root.attrib.get("uid")
    timestamp = root.attrib.get("time")
    point = root.find("point")

    lat = overrides.get("lat") if overrides else point.attrib.get("lat")
    lon = overrides.get("lon") if overrides else point.attrib.get("lon")
    hae = overrides.get("alt") if overrides else point.attrib.get("hae")

    cot = ET.Element("event")
    cot.attrib = {
        "version": "2.0",
        "uid": uid or "UNKNOWN",
        "type": "a-f-G-U-C",  # placeholder type
        "how": "m-g",
        "time": timestamp,
        "start": timestamp,
        "stale": timestamp
    }
    point_elem = ET.SubElement(cot, "point", {
        "lat": lat or "0.0",
        "lon": lon or "0.0",
        "hae": hae or "0.0",
        "ce": "9999999.0",
        "le": "9999999.0"
    })

    return ET.tostring(cot, encoding="unicode")


def to_json(root, overrides=None):
    uid = root.attrib.get("uid") if root.tag == "event" else "UNKNOWN"
    timestamp = root.attrib.get("time", "UNKNOWN")
    point = root.find("point")

    lat = point.attrib.get("lat") if point is not None else "0"
    lon = point.attrib.get("lon") if point is not None else "0"
    alt = point.attrib.get("hae") if point is not None else "0"

    data = {
        "uid": overrides.get("uid", uid) if overrides else uid,
        "timestamp": timestamp,
        "lat": overrides.get("lat", lat) if overrides else lat,
        "lon": overrides.get("lon", lon) if overrides else lon,
        "alt": overrides.get("alt", alt) if overrides else alt,
    }

    return json.dumps(data, indent=2)
