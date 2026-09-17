# Image Metadata Injector: EXIF GPS, IPTC, XMP & PDF Variant Hash Generator
import sys, os
from datetime import datetime

# Include vendor_py for Pillow and piexif
vendor_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'vendor_py')
if os.path.exists(vendor_dir) and vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)

from PIL import Image, ImageEnhance
import piexif
from .registry import DEFAULT_BUSINESS, get_city_geo, decimal_to_dms_rational

def build_xmp_packet(title, caption, keywords, city, state, country, business):
    kw_lis = "".join(f"<rdf:li>{kw.strip()}</rdf:li>" for kw in keywords if kw.strip())
    now_iso = datetime.now().isoformat()
    xmp = f"""<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Gold Standard Geo Media Engine 1.0">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/"
    xmlns:xmp="http://ns.adobe.com/xap/1.0/">
   <dc:title>
    <rdf:Alt>
     <rdf:li xml:lang="x-default">{title}</rdf:li>
    </rdf:Alt>
   </dc:title>
   <dc:description>
    <rdf:Alt>
     <rdf:li xml:lang="x-default">{caption}</rdf:li>
    </rdf:Alt>
   </dc:description>
   <dc:creator>
    <rdf:Seq>
     <rdf:li>{business['legal_name']}</rdf:li>
    </rdf:Seq>
   </dc:creator>
   <dc:subject>
    <rdf:Bag>
     {kw_lis}
    </rdf:Bag>
   </dc:subject>
   <photoshop:City>{city}</photoshop:City>
   <photoshop:State>{state}</photoshop:State>
   <photoshop:Country>{country}</photoshop:Country>
   <photoshop:Credit>{business['name']}</photoshop:Credit>
   <photoshop:Source>{business['website']}</photoshop:Source>
   <photoshop:TransmissionReference>{business['cid']}</photoshop:TransmissionReference>
   <photoshop:Instructions>Google Maps CID: {business['cid_url']}</photoshop:Instructions>
   <dc:identifier>{business['cid_url']}</dc:identifier>
   <xmp:CreateDate>{now_iso}</xmp:CreateDate>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>"""
    return xmp.encode('utf-8')

def inject_image_metadata(input_path, output_path, service, city_name, heading, keywords=None, business=None):
    business = business or DEFAULT_BUSINESS
    geo = get_city_geo(city_name)
    keywords = keywords or [service, f"{service} {geo['name']}", f"{geo['name']} Local SEO", "Google Maps 3-Pack", geo['county']]

    img = Image.open(input_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Standardize web resolution (1200 max width, maintaining aspect ratio)
    orig_w, orig_h = img.size
    max_w = 1200
    if orig_w > max_w:
        ratio = max_w / float(orig_w)
        target_size = (max_w, int(float(orig_h) * ratio))
        img = img.resize(target_size, Image.Resampling.LANCZOS)

    # Prepare EXIF GPS
    lat = geo['lat']
    lon = geo['lon']
    alt_m = geo['altitude_m']

    lat_ref = 'N' if lat >= 0 else 'S'
    lon_ref = 'E' if lon >= 0 else 'W'
    lat_dms = decimal_to_dms_rational(lat)
    lon_dms = decimal_to_dms_rational(lon)

    now_str = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
    caption = f"{heading} by {business['name']}. Located in {geo['name']}, {geo['state']} {geo['zip_codes'][0]}. Google Maps CID: {business['cid_url']}. Call {business['display_phone']} for regional Google Maps 3-Pack & Local SEO dominance."

    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: lat_ref,
        piexif.GPSIFD.GPSLatitude: lat_dms,
        piexif.GPSIFD.GPSLongitudeRef: lon_ref,
        piexif.GPSIFD.GPSLongitude: lon_dms,
        piexif.GPSIFD.GPSAltitudeRef: 0,
        piexif.GPSIFD.GPSAltitude: (int(alt_m), 1),
        piexif.GPSIFD.GPSDateStamp: datetime.now().strftime("%Y:%m:%d")
    }

    zeroth_ifd = {
        piexif.ImageIFD.Make: b"Gold Standard Assets",
        piexif.ImageIFD.Model: b"Geo-Targeted Authority Asset",
        piexif.ImageIFD.Artist: business['legal_name'].encode('utf-8'),
        piexif.ImageIFD.Copyright: f"© 2026 {business['legal_name']}. All rights reserved.".encode('utf-8'),
        piexif.ImageIFD.ImageDescription: caption.encode('utf-8'),
        piexif.ImageIFD.Software: b"Gold Standard Local SEO & GEO Engine",
        piexif.ImageIFD.DateTime: now_str.encode('utf-8')
    }

    exif_ifd = {
        piexif.ExifIFD.DateTimeOriginal: now_str.encode('utf-8'),
        piexif.ExifIFD.DateTimeDigitized: now_str.encode('utf-8'),
        piexif.ExifIFD.UserComment: caption.encode('utf-8')
    }

    exif_dict = {"0th": zeroth_ifd, "Exif": exif_ifd, "GPS": gps_ifd}
    exif_bytes = piexif.dump(exif_dict)

    # Save initial JPEG with EXIF
    img.save(output_path, 'JPEG', quality=92, exif=exif_bytes, optimize=True)

    # Inject XMP packet into APP1 segment
    xmp_bytes = build_xmp_packet(heading, caption, keywords, geo['name'], geo['state'], business['country'], business)
    _inject_xmp_into_jpeg(output_path, xmp_bytes)

    return {
        "output_path": output_path,
        "dimensions": img.size,
        "city": geo['name'],
        "coordinates": (lat, lon),
        "caption": caption
    }

def _inject_xmp_into_jpeg(jpeg_path, xmp_bytes):
    with open(jpeg_path, 'rb') as f:
        data = f.read()

    if data[:2] != b'\xff\xd8':
        return

    # Construct APP1 XMP marker
    header = b'http://ns.adobe.com/xap/1.0/\x00'
    payload = header + xmp_bytes
    marker_len = len(payload) + 2
    app1_marker = b'\xff\xe1' + marker_len.to_bytes(2, 'big') + payload

    # Insert right after SOI (FF D8)
    new_data = data[:2] + app1_marker + data[2:]
    with open(jpeg_path, 'wb') as f:
        f.write(new_data)

def create_pdf_variant_image(input_img_path, output_variant_path):
    # Generates a distinct variant for the PDF:
    # 1. Subtle crop (removes 3% edges) -> distinct aspect ratio
    # 2. Subtle contrast boost (+3%) -> distinct perceptual hash (pHash)
    # 3. 300 DPI document raster format
    img = Image.open(input_img_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    w, h = img.size
    crop_x = int(w * 0.03)
    crop_y = int(h * 0.03)
    cropped = img.crop((crop_x, crop_y, w - crop_x, h - crop_y))

    enhancer = ImageEnhance.Contrast(cropped)
    enhanced = enhancer.enhance(1.04)

    enhanced.save(output_variant_path, 'JPEG', quality=95, dpi=(300, 300))
    return output_variant_path
