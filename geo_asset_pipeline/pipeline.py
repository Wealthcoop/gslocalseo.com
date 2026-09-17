# Unified Geo-Asset Automation Pipeline for Images and Videos
import os, sys, json
from datetime import datetime

# Include vendor_py
vendor_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'vendor_py')
if os.path.exists(vendor_dir) and vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)

from .registry import DEFAULT_BUSINESS, get_city_geo
from .content_engine import generate_content_bundle
from .metadata_injector import inject_image_metadata, create_pdf_variant_image
from .video_injector import inject_video_metadata
from .pdf_builder import build_companion_pdf

def is_video_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    return ext in ['.mp4', '.mov', '.m4v', '.webm', '.avi']

def process_geo_asset(
    input_path,
    service="Local SEO & Google Maps Optimization",
    city="Folsom",
    heading="The 4 Proprietary Systems of Local Dominance",
    output_dir="./geo_dist",
    business=None
):
    business = business or DEFAULT_BUSINESS
    geo = get_city_geo(city)
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input asset not found: {input_path}")

    # 1. Generate Dual-Search Content Bundle
    bundle = generate_content_bundle(service, geo['name'], heading, business=business)
    seo_slug = bundle['seo_slug']
    alt_text = bundle['alt_text']
    article = bundle['article']

    pdf_filename = f"{seo_slug}-geo-authority.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)

    is_vid = is_video_file(input_path)

    if is_vid:
        # Video Processing Branch
        out_video_name = f"{seo_slug}.mp4"
        out_video_path = os.path.join(output_dir, out_video_name)
        
        vid_res = inject_video_metadata(input_path, out_video_path, service, geo['name'], heading, business=business)
        
        poster_path = vid_res['poster_path']
        variant_img_path = vid_res['pdf_variant_path']
        video_schema = vid_res['schema_video']

        # Build Companion Geo-PDF
        build_companion_pdf(
            output_pdf_path=pdf_path,
            variant_image_path=variant_img_path,
            content_bundle=bundle,
            service=service,
            city_name=geo['name'],
            heading=heading,
            business=business
        )

        poster_rel = os.path.basename(poster_path)
        video_rel = os.path.basename(out_video_path)

        # Build Embed Snippet
        html_snippet = f"""<!-- Geo-Optimized Video & Companion PDF Embed -->
<figure class="geo-asset-card geo-video-card" style="margin: 2rem 0; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; background: #ffffff; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
  <div style="position: relative; width: 100%; aspect-ratio: 16/9; background: #0f172a;">
    <video controls poster="/assets/{poster_rel}" style="width: 100%; height: 100%; object-fit: cover; display: block;" preload="metadata">
      <source src="/assets/{video_rel}" type="video/mp4">
      Your browser does not support the video tag.
    </video>
  </div>
  <figcaption style="padding: 1.25rem; font-family: system-ui, -apple-system, sans-serif;">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.75rem;">
      <span style="display: inline-flex; align-items: center; gap: 0.35rem; font-size: 0.75rem; font-weight: 700; color: #b45309; background: #fef3c7; padding: 0.25rem 0.6rem; border-radius: 9999px; text-transform: uppercase;">
        📍 {geo['name']}, CA • Geo-Targeted
      </span>
      <span style="font-size: 0.8rem; color: #64748b;">
        GPS: {geo['lat']}, {geo['lon']}
      </span>
    </div>
    <h3 style="font-size: 1.15rem; font-weight: 700; color: #0f172a; margin: 0 0 0.5rem 0;">{heading}</h3>
    <p style="font-size: 0.875rem; color: #475569; margin: 0 0 1rem 0; line-height: 1.5;">
      {alt_text}
    </p>
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem; padding-top: 0.75rem; border-top: 1px solid #f1f5f9;">
      <a href="/assets/{pdf_filename}" target="_blank" rel="noopener noreferrer" style="display: inline-flex; align-items: center; gap: 0.5rem; background: #0f172a; color: #ffffff; font-size: 0.85rem; font-weight: 600; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none;">
        📄 Download Verified Geo-Authority Report (PDF)
      </a>
      <a href="{business['cid_url']}" target="_blank" rel="noopener noreferrer" style="font-size: 0.825rem; font-weight: 600; color: #2563eb; text-decoration: none;">
        🗺️ Verify Google Maps Entity ({business['cid']}) →
      </a>
    </div>
  </figcaption>
</figure>

<!-- Schema.org VideoObject Rich Snippet -->
<script type="application/ld+json">
{json.dumps(video_schema, indent=2)}
</script>
"""
        manifest = {
            "type": "video",
            "service": service,
            "city": geo['name'],
            "coordinates": (geo['lat'], geo['lon']),
            "heading": heading,
            "output_video": out_video_path,
            "poster_frame": poster_path,
            "pdf_variant": variant_img_path,
            "companion_pdf": pdf_path,
            "pdf_word_count": article['word_count'],
            "article_title": article['article_title'],
            "focus_type": article['focus_type'],
            "schema": video_schema
        }

    else:
        # Image Processing Branch
        out_image_name = f"{seo_slug}.jpg"
        out_image_path = os.path.join(output_dir, out_image_name)
        variant_img_name = f"{seo_slug}-variant.jpg"
        variant_img_path = os.path.join(output_dir, variant_img_name)

        # 1. Inject EXIF GPS, IPTC, XMP into output image
        img_res = inject_image_metadata(
            input_path,
            out_image_path,
            service=service,
            city_name=geo['name'],
            heading=heading,
            keywords=bundle['keywords'],
            business=business
        )

        # 2. Create distinct PDF variant (3% crop, 1.04 contrast, 300 DPI)
        create_pdf_variant_image(out_image_path, variant_img_path)

        # 3. Build Companion Geo-PDF
        build_companion_pdf(
            output_pdf_path=pdf_path,
            variant_image_path=variant_img_path,
            content_bundle=bundle,
            service=service,
            city_name=geo['name'],
            heading=heading,
            business=business
        )

        image_rel = os.path.basename(out_image_path)

        # Build Embed Snippet
        html_snippet = f"""<!-- Geo-Optimized Image & Companion PDF Embed -->
<figure class="geo-asset-card" style="margin: 2rem 0; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; background: #ffffff; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
  <a href="/assets/{pdf_filename}" target="_blank" rel="noopener noreferrer" style="display: block; overflow: hidden;">
    <img src="/assets/{image_rel}" alt="{alt_text}" loading="lazy" style="width: 100%; height: auto; display: block; object-fit: cover; transition: transform 0.3s ease;">
  </a>
  <figcaption style="padding: 1.25rem; font-family: system-ui, -apple-system, sans-serif;">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.75rem;">
      <span style="display: inline-flex; align-items: center; gap: 0.35rem; font-size: 0.75rem; font-weight: 700; color: #b45309; background: #fef3c7; padding: 0.25rem 0.6rem; border-radius: 9999px; text-transform: uppercase;">
        📍 {geo['name']}, CA • Geo-Targeted
      </span>
      <span style="font-size: 0.8rem; color: #64748b;">
        GPS: {geo['lat']}, {geo['lon']}
      </span>
    </div>
    <h3 style="font-size: 1.15rem; font-weight: 700; color: #0f172a; margin: 0 0 0.5rem 0;">{heading}</h3>
    <p style="font-size: 0.875rem; color: #475569; margin: 0 0 1rem 0; line-height: 1.5;">
      {alt_text}
    </p>
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem; padding-top: 0.75rem; border-top: 1px solid #f1f5f9;">
      <a href="/assets/{pdf_filename}" target="_blank" rel="noopener noreferrer" style="display: inline-flex; align-items: center; gap: 0.5rem; background: #0f172a; color: #ffffff; font-size: 0.85rem; font-weight: 600; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none;">
        📄 Download Verified Geo-Authority Report (PDF)
      </a>
      <a href="{business['cid_url']}" target="_blank" rel="noopener noreferrer" style="font-size: 0.825rem; font-weight: 600; color: #2563eb; text-decoration: none;">
        🗺️ Verify Google Maps Entity ({business['cid']}) →
      </a>
    </div>
  </figcaption>
</figure>
"""
        manifest = {
            "type": "image",
            "service": service,
            "city": geo['name'],
            "coordinates": (geo['lat'], geo['lon']),
            "heading": heading,
            "output_image": out_image_path,
            "pdf_variant": variant_img_path,
            "companion_pdf": pdf_path,
            "pdf_word_count": article['word_count'],
            "article_title": article['article_title'],
            "focus_type": article['focus_type']
        }

    # Save manifest and html snippet
    snippet_file = os.path.join(output_dir, f"{seo_slug}-embed.html")
    manifest_file = os.path.join(output_dir, f"{seo_slug}-manifest.json")

    with open(snippet_file, "w", encoding="utf-8") as f:
        f.write(html_snippet)

    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    manifest["snippet_file"] = snippet_file
    manifest["manifest_file"] = manifest_file
    manifest["html_snippet"] = html_snippet
    return manifest
