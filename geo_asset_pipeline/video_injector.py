# Video Metadata Injector: MP4 Container Atom Injection, Poster Extraction & VideoObject Schema
import os, subprocess, json
from datetime import datetime
from .registry import DEFAULT_BUSINESS, get_city_geo, format_iso6709
from .metadata_injector import inject_image_metadata, create_pdf_variant_image

FFMPEG_BIN = "/usr/local/bin/ffmpeg"
FFPROBE_BIN = "/usr/local/bin/ffprobe"

def extract_poster_frame(video_path, output_poster_path, timestamp="00:00:03"):
    cmd = [
        FFMPEG_BIN, "-y",
        "-ss", timestamp,
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "2",
        output_poster_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        # Fallback to second 0
        cmd_fallback = [FFMPEG_BIN, "-y", "-ss", "00:00:00.5", "-i", video_path, "-vframes", "1", "-q:v", "2", output_poster_path]
        subprocess.run(cmd_fallback, capture_output=True, text=True)
    return output_poster_path

def get_video_duration(video_path):
    cmd = [
        FFPROBE_BIN, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        return float(res.stdout.strip())
    except Exception:
        return 60.0

def inject_video_metadata(input_video_path, output_video_path, service, city_name, heading, business=None):
    business = business or DEFAULT_BUSINESS
    geo = get_city_geo(city_name)
    iso_location = format_iso6709(geo['lat'], geo['lon'], geo['altitude_m'])
    duration_secs = get_video_duration(input_video_path)

    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    description = f"{heading} by {business['name']}. Geo-Targeted in {geo['name']}, {geo['state']} {geo['zip_codes'][0]}. Official Google Maps CID: {business['cid_url']}. Call {business['display_phone']} for 3-Pack prominence."
    comment = f"NAP: {business['name']} | {business['street_address']}, {business['city']}, {business['state']} {business['postal_code']} | Tel: {business['display_phone']}"
    copyright_str = f"© 2026 {business['legal_name']}. All rights reserved."

    cmd = [
        FFMPEG_BIN, "-y",
        "-i", input_video_path,
        "-c", "copy",
        "-metadata", f"title={heading}",
        "-metadata", f"description={description}",
        "-metadata", f"artist={business['legal_name']}",
        "-metadata", f"album_artist={business['name']}",
        "-metadata", f"comment={comment}",
        "-metadata", f"copyright={copyright_str}",
        "-metadata", f"genre=Local SEO & Google Maps Marketing",
        "-metadata", f"location={iso_location}",
        "-metadata", f"location-eng={iso_location}",
        "-metadata", f"date={now_iso}",
        "-movflags", "+faststart",
        output_video_path
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg failed to inject metadata into {input_video_path}: {res.stderr}")

    # Extract & inject metadata into poster frame
    base_no_ext = os.path.splitext(output_video_path)[0]
    poster_path = f"{base_no_ext}-poster.jpg"
    extract_poster_frame(output_video_path, poster_path)

    # Inject EXIF/IPTC/XMP into poster
    inject_image_metadata(poster_path, poster_path, service, geo['name'], heading, business=business)

    # Generate distinct PDF variant
    pdf_variant_path = f"{base_no_ext}-pdf-variant.jpg"
    create_pdf_variant_image(poster_path, pdf_variant_path)

    # Build schema.org/VideoObject JSON-LD
    filename = os.path.basename(output_video_path)
    poster_filename = os.path.basename(poster_path)
    schema_video = {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": heading,
        "description": description,
        "thumbnailUrl": f"{business['website']}/assets/{poster_filename}",
        "contentUrl": f"{business['website']}/assets/{filename}",
        "uploadDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "duration": f"PT{int(duration_secs)}S",
        "contentLocation": {
            "@type": "Place",
            "name": f"{geo['name']}, {geo['state']}",
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": geo['lat'],
                "longitude": geo['lon']
            }
        },
        "publisher": {
            "@type": "LocalBusiness",
            "name": business['name'],
            "telephone": business['phone'],
            "url": business['website'],
            "address": {
                "@type": "PostalAddress",
                "streetAddress": business['street_address'],
                "addressLocality": business['city'],
                "addressRegion": business['state'],
                "postalCode": business['postal_code'],
                "addressCountry": business['country']
            }
        }
    }

    return {
        "video_path": output_video_path,
        "poster_path": poster_path,
        "pdf_variant_path": pdf_variant_path,
        "schema_video": schema_video,
        "iso_location": iso_location,
        "duration": duration_secs
    }
