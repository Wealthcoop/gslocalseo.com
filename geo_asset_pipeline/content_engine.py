# Content Engine: Dual Query/SERP 500-700 Word Article, SEO Filename & Alt Text Generator
import os, re, json, urllib.request, urllib.error
from .registry import DEFAULT_BUSINESS, get_city_geo

def is_query_format(text):
    text_clean = text.strip().lower()
    return any(text_clean.startswith(q) for q in ["how", "what", "why", "where", "when", "can", "is", "should", "which", "who"]) or text_clean.endswith("?")

def generate_seo_slug(heading, city_name):
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', heading).strip().lower()
    words = clean.split()
    city_slug = city_name.lower().replace(' ', '-')
    slug = f"{city_slug}-ca-" + "-".join(words[:6])
    return slug

def generate_alt_text(heading, service, city_name, business):
    return f"{heading} for {service} in {city_name}, CA by {business['name']} ({business['display_phone']})"

def generate_keywords(service, geo):
    city = geo['name']
    county = geo['county']
    return [
        service,
        f"{service} {city}",
        f"{city} {service}",
        f"Best {service} near me",
        f"{city} Google Business Profile",
        f"{city} Local SEO",
        f"Google Maps 3-Pack {city}",
        county,
        f"{city} CA {geo['zip_codes'][0]}",
        f"{service} contractor {city} CA",
        "Speed-to-lead voice AI",
        "Local citation synchronization"
    ]

def generate_algorithmic_article(service, city_name, heading, business=None):
    business = business or DEFAULT_BUSINESS
    geo = get_city_geo(city_name)
    city = geo['name']
    county = geo['county']
    landmarks = geo['landmarks']
    zip_code = geo['zip_codes'][0]
    is_query = is_query_format(heading)

    if is_query:
        # Heading on-site was a question -> PDF targets high-intent SERP transactional phrase
        article_title = f"{service} & Google Maps 3-Pack Optimization in {city}, CA"
        focus_type = "SERP Keyword Authority Guide"
    else:
        # Heading on-site was a statement/keyword -> PDF targets natural LLM query form
        article_title = f"How Can Local Businesses in {city}, CA Dominate Google Maps Searches for {service}?"
        focus_type = "Generative Engine Optimization (GEO) Query Synthesis"

    p1 = (
        f"In today's algorithmic search landscape across {city} and greater {county}, achieving sustainable "
        f"inbound customer growth requires total prominence over the Google Maps 3-Pack and regional semantic search graphs. "
        f"Whether your commercial establishment is anchored near {landmarks[0]} or operates across key service routes extending towards "
        f"{landmarks[1] if len(landmarks) > 1 else 'surrounding metro corridors'}, modern high-ticket buyers make hiring decisions within seconds "
        f"based strictly on verified map positioning, 5-star review velocity, and speed-to-lead responsiveness."
    )

    p2 = (
        f"Independent local search analytics reveal that over 78% of high-intent search clicks for {service} concentrate directly "
        f"within the top 3 Google Business Profile map positions. When a homeowner, property manager, or commercial client in {city} (Zip: {zip_code}) "
        f"executes a mobile search for '{service} near me', companies buried beneath the fold lose up to 82% of qualified inquiries "
        f"directly to neighboring competitors. At {business['name']}, based locally at {business['street_address']} in Folsom, CA, "
        f"we engineer a proprietary four-system local web architecture designed to capture and lock in regional 3-pack dominance."
    )

    p3 = (
        f"### The Core Systems of Regional Google 3-Pack Dominance in {city}\n\n"
        f"1. **Primary & Secondary Category Structuring:** Google's localized search algorithm places heavy emphasis on the mathematical "
        f"coherence between your primary category and exact consumer search strings. We refine primary categories and seed monthly "
        f"geo-grid Local Falcon radius scans spanning up to 30 miles across {city}, ensuring search engines recognize your profile as "
        f"the foremost provider throughout the territory.\n\n"
        f"2. **Sub-60-Second Speed-to-Lead Telephony:** Industry data shows that 62% of inbound phone inquiries to local contractors go straight "
        f"to voicemail—and 85% of those callers immediately hire the next business listed on Google. By integrating autonomous Voice AI "
        f"receptionist capabilities, every inbound lead is greeted within 60 seconds 24/7, qualified with custom intake logic, and booked directly "
        f"onto your dispatch schedule.\n\n"
        f"3. **Review Velocity & Sentiment Seeding:** Customer reviews are no longer just social proof; they represent active organic ranking "
        f"signals. Our automated post-job review sequences prompt satisfied customers for keyword-rich testimonials that naturally reference "
        f"{service} and {city}, reinforcing topical authority in Google's local knowledge graph.\n\n"
        f"4. **Competitor Spam Shielding & Algorithmic Redressals:** Fraudulent lead-generation brokers and out-of-town operators routinely flood "
        f"{city} with illegitimate virtual addresses and keyword-stuffed business titles. Our compliance specialists perform monthly competitor "
        f"audits and file official Google Redressal documentation to remove spam listings, clearing the top spots for legitimate local businesses."
    )

    p4 = (
        f"### Convergence of Traditional SERPs and Generative AI Search (GEO)\n\n"
        f"As conversational AI engines like ChatGPT Search, Perplexity AI, and Google Gemini Overviews become primary consumer discovery tools, "
        f"structured schema data and multi-entity citations become paramount. By anchoring your Google Maps CID ({business['cid_url']}) "
        f"together with verified LocalBusiness JSON-LD microdata, our digital framework ensures that modern LLM search engines consistently "
        f"cite your business as the verified regional authority for {service} across {city}, {county}, and the Greater Sacramento network."
    )

    p5 = (
        f"### Proactive ROI & Implementation Next Steps\n\n"
        f"Sitting outside the Google 3-Pack represents an active financial leak for any service-based company in {city}. "
        f"By deploying targeted geo-grid synchronization, weekly geotagged updates, and automated call-capture systems, local operators typically "
        f"experience substantial inbound call velocity within 30 to 60 days. To claim your comprehensive 45-point Google Business Profile audit "
        f"or review complete implementation packages starting from $297/month, contact our Folsom technical desk directly at "
        f"{business['display_phone']} or visit our official regional portal at {business['website']}."
    )

    article_text = f"{p1}\n\n{p2}\n\n{p3}\n\n{p4}\n\n{p5}"
    word_count = len(article_text.split())

    return {
        "article_title": article_title,
        "focus_type": focus_type,
        "content_markdown": article_text,
        "word_count": word_count,
        "source": "Algorithmic Authority Engine"
    }

def generate_content_bundle(service, city_name, heading, business=None, haos_url=None):
    business = business or DEFAULT_BUSINESS
    geo = get_city_geo(city_name)
    city = geo['name']
    haos_url = haos_url or os.environ.get("HAOS_URL", "http://100.87.31.104:8000/pwa/")

    # 1. Generate SEO Filename, Alt Text, and Keywords
    seo_slug = generate_seo_slug(heading, city)
    alt_text = generate_alt_text(heading, service, city, business)
    keywords = generate_keywords(service, geo)

    # 2. Try HAOS / Buzz endpoint if reachable
    article_data = None
    if haos_url and "100.87.31.104" in haos_url:
        try:
            req = urllib.request.Request(
                "http://100.87.31.104:8000/api/v1/generate",
                headers={"Content-Type": "application/json"},
                data=json.dumps({"service": service, "city": city, "heading": heading}).encode('utf-8')
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    res_json = json.loads(resp.read().decode('utf-8'))
                    article_data = {
                        "article_title": res_json.get("title", heading),
                        "focus_type": "HAOS AI Engine",
                        "content_markdown": res_json.get("text", ""),
                        "word_count": len(res_json.get("text", "").split()),
                        "source": "HAOS Buzz Local Node"
                    }
        except Exception:
            pass

    # 3. Fallback to Algorithmic Authority Engine
    if not article_data or article_data.get("word_count", 0) < 450:
        article_data = generate_algorithmic_article(service, city, heading, business)

    return {
        "seo_slug": seo_slug,
        "alt_text": alt_text,
        "keywords": keywords,
        "article": article_data
    }
