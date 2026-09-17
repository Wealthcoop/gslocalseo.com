#!/usr/bin/env python3
"""
Gold Standard Geo-Asset Pipeline CLI
Processes images and videos into geo-targeted, search-optimized assets paired with companion PDFs.
"""
import sys, os, argparse

# Ensure local workspace vendor libraries are loaded
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENDOR_DIR = os.path.join(BASE_DIR, "vendor_py")
if os.path.exists(VENDOR_DIR) and VENDOR_DIR not in sys.path:
    sys.path.insert(0, VENDOR_DIR)

from geo_asset_pipeline.pipeline import process_geo_asset
from geo_asset_pipeline.registry import CITIES

def main():
    city_names = [c['name'] for c in CITIES.values()]
    parser = argparse.ArgumentParser(
        description="Gold Standard Geo-Asset & PDF Automation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process an Image:
  python3 run_geo_pipeline.py --input ./gold-standard-logo.png --city Folsom --heading "The 4 Proprietary Systems of Local Dominance"

  # Process a Video:
  python3 run_geo_pipeline.py --input ./promo.mp4 --city Roseville --service "Google Maps 3-Pack Optimization" --heading "How Can Local Businesses in Roseville Dominate Google Maps?"
        """
    )
    parser.add_argument("--input", "-i", required=True, help="Path to input image (.jpg, .png, .webp) or video (.mp4, .mov)")
    parser.add_argument("--city", "-c", default="Folsom", help=f"Target Northern California city (Default: Folsom). Available: {', '.join(city_names)}")
    parser.add_argument("--service", "-s", default="Local SEO & Google Maps Optimization", help="Target service keyword phrase")
    parser.add_argument("--heading", "-H", default="The 4 Proprietary Systems of Local Dominance", help="On-site heading or section title")
    parser.add_argument("--output", "-o", default="./geo_dist", help="Output directory for generated assets (Default: ./geo_dist)")

    args = parser.parse_args()

    print(f"\n🚀 [Gold Standard Geo-Pipeline] Initializing...")
    print(f" • Input File : {args.input}")
    print(f" • Target City: {args.city}")
    print(f" • Service    : {args.service}")
    print(f" • Heading    : {args.heading}")
    print(f" • Output Dir : {args.output}\n")

    try:
        manifest = process_geo_asset(
            input_path=args.input,
            service=args.service,
            city=args.city,
            heading=args.heading,
            output_dir=args.output
        )

        print("✅ [Pipeline Success] Asset processed and paired successfully!")
        print(f" • Asset Type   : {manifest['type'].upper()}")
        print(f" • Target Geo   : {manifest['city']}, CA (GPS: {manifest['coordinates'][0]}, {manifest['coordinates'][1]})")
        print(f" • Article Title: {manifest['article_title']}")
        print(f" • Focus Engine : {manifest['focus_type']}")
        print(f" • Companion PDF: {manifest['companion_pdf']} ({manifest['pdf_word_count']} words)")
        print(f" • HTML Snippet : {manifest['snippet_file']}")
        print(f" • Manifest     : {manifest['manifest_file']}\n")

        print("📋 Embed Code Preview:")
        print("--------------------------------------------------------------------------------")
        print(manifest['html_snippet'][:500] + "...\n(Full embed snippet saved in " + manifest['snippet_file'] + ")")
        print("--------------------------------------------------------------------------------\n")

    except Exception as e:
        print(f"\n❌ [Error] Failed to process geo-asset: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
