import re
import unicodedata
from collections import defaultdict


UNCLASSIFIED_AREA = "Multidisciplinary / Unclassified"

THEMATIC_AREAS = (
    "Agriculture",
    "Engineering",
    "Health Sciences",
    "Humanities",
    "Law",
    "Natural Sciences",
    "Social Sciences",
)

# Deliberately high-precision vocabulary. Broad institutional metadata is
# weighted below titles and provider topics, so an author's department helps
# with an otherwise ambiguous paper without overruling paper-level evidence.
AREA_KEYWORDS = {
    "Agriculture": (
        "agriculture",
        "agricultural",
        "agronomy",
        "agroforestry",
        "crop",
        "crops",
        "plant breeding",
        "soil fertility",
        "irrigation",
        "horticulture",
        "livestock",
        "poultry",
        "fisheries",
        "aquaculture",
        "food security",
        "farm",
        "farming",
        "cassava",
        "maize",
        "cocoa",
        "yam",
        "cowpea",
    ),
    "Engineering": (
        "engineering",
        "computer science",
        "computing",
        "software",
        "algorithm",
        "artificial intelligence",
        "machine learning",
        "deep learning",
        "cybersecurity",
        "computer vision",
        "face recognition",
        "image recognition",
        "information system",
        "telecommunication",
        "robotics",
        "electronics",
        "electrical",
        "mechanical",
        "civil engineering",
        "materials science",
        "renewable energy",
        "energy system",
        "construction",
        "architecture",
    ),
    "Health Sciences": (
        "health",
        "medicine",
        "medical",
        "disease",
        "clinical",
        "epidemiology",
        "nursing",
        "midwifery",
        "pharmacy",
        "pharmacology",
        "therapeutic",
        "surgery",
        "pathology",
        "public health",
        "malaria",
        "hiv",
        "tuberculosis",
        "cancer",
        "virus",
        "viral",
        "bacteria",
        "microbiology",
        "parasite",
        "immunology",
        "nutrition",
        "physiology",
        "biomedical",
        "dentistry",
        "dental",
        "mortality",
        "prevalence",
        "tobacco",
        "nicotine",
        "patient",
        "maternal",
        "paediatric",
        "pediatric",
    ),
    "Humanities": (
        "humanities",
        "history",
        "historical",
        "literature",
        "literary",
        "language",
        "linguistics",
        "philosophy",
        "religion",
        "theology",
        "archaeology",
        "heritage",
        "music",
        "theatre",
        "dance",
        "visual art",
        "cultural studies",
        "arts and humanities",
    ),
    "Law": (
        "law",
        "legal",
        "judicial",
        "court",
        "constitutional",
        "human rights",
        "jurisprudence",
        "legislation",
        "criminal justice",
    ),
    "Natural Sciences": (
        "natural science",
        "natural sciences",
        "life science",
        "life sciences",
        "physical science",
        "physical sciences",
        "physical and mathematical sciences",
        "biology",
        "biological",
        "chemistry",
        "chemical",
        "physics",
        "astronomy",
        "mathematics",
        "mathematical",
        "statistics",
        "statistical",
        "actuarial",
        "time series",
        "probability",
        "probabilistic",
        "geology",
        "earth science",
        "environmental science",
        "ecology",
        "ecological",
        "climate change",
        "biodiversity",
        "conservation",
        "biochemistry",
        "genetics",
        "molecular",
        "cell biology",
        "quantum",
        "marine science",
    ),
    "Social Sciences": (
        "social science",
        "social sciences",
        "economics",
        "economic",
        "finance",
        "financial",
        "accounting",
        "business",
        "management",
        "marketing",
        "entrepreneurship",
        "political",
        "politics",
        "governance",
        "public administration",
        "sociology",
        "social",
        "psychology",
        "education",
        "teacher",
        "population",
        "demography",
        "election",
        "electoral",
        "geography",
        "human geography",
        "migration",
        "gender",
        "development studies",
        "urban",
        "urban studies",
        "foreign direct investment",
        "inflation",
        "exchange rate",
        "stock return",
        "stock returns",
        "stock market",
        "equity market",
        "econometric",
        "cointegration",
        "transport",
        "transportation",
        "communication",
        "media studies",
        "anthropology",
        "human resource",
        "tourism",
    ),
}


def _normalize(value):
    value = unicodedata.normalize("NFKD", str(value or ""))
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


NORMALIZED_AREA_KEYWORDS = {
    area: tuple((keyword, _normalize(keyword)) for keyword in keywords)
    for area, keywords in AREA_KEYWORDS.items()
}


def _topic_text(topic):
    if isinstance(topic, str):
        return topic
    if not isinstance(topic, dict):
        return ""
    values = [
        topic.get("name"),
        topic.get("display_name"),
        topic.get("subfield"),
        topic.get("field"),
        topic.get("domain"),
    ]
    return " ".join(
        value.get("display_name", "") if isinstance(value, dict) else str(value or "")
        for value in values
    )


def _profile_interests(profile):
    interests = getattr(profile, "interests", None) or []
    interest_names = []
    for interest in interests:
        if isinstance(interest, dict):
            interest_names.append(
                interest.get("title") or interest.get("display_name") or ""
            )
        else:
            interest_names.append(str(interest))
    return " ".join(interest_names)


def classify_publication_metadata(
    *,
    title="",
    journal="",
    provider_topics=None,
    profiles=None,
):
    """Classify a publication using transparent, weighted metadata signals."""

    scores = defaultdict(float)
    matches = defaultdict(list)

    def add_signal(signal, text, base_weight):
        normalized_value = _normalize(text)
        if not normalized_value:
            return
        normalized_text = f" {normalized_value} "
        for area, keywords in NORMALIZED_AREA_KEYWORDS.items():
            for keyword, normalized_keyword in keywords:
                if f" {normalized_keyword} " not in normalized_text:
                    continue
                # Multi-word phrases are more discriminating than single words.
                specificity = 1 + min(normalized_keyword.count(" ") * 0.25, 0.75)
                points = base_weight * specificity
                scores[area] += points
                matches[area].append(
                    {
                        "signal": signal,
                        "term": keyword,
                        "points": round(points, 2),
                    }
                )

    topics = provider_topics or []
    for index, topic in enumerate(topics):
        if isinstance(topic, dict):
            try:
                topic_score = float(topic.get("score", 1) or 1)
            except (TypeError, ValueError):
                topic_score = 1
            is_primary = bool(topic.get("primary")) or index == 0
        else:
            topic_score = 1
            is_primary = index == 0
        topic_weight = (7 if is_primary else 4) * max(0.25, min(topic_score, 1))
        add_signal(
            "primary_provider_topic" if is_primary else "provider_topic",
            _topic_text(topic),
            topic_weight,
        )

    add_signal("title", title, 5)
    add_signal("journal", journal, 2)
    for profile in profiles or []:
        add_signal(
            "author_department",
            getattr(profile, "department", "") or "",
            1.25,
        )
        add_signal(
            "author_school",
            getattr(profile, "school", "") or "",
            0.9,
        )
        add_signal("author_interests", _profile_interests(profile), 0.75)
        add_signal(
            "author_college",
            getattr(profile, "college", "") or "",
            0.5,
        )

    ranked = sorted(
        scores.items(),
        key=lambda item: (-item[1], THEMATIC_AREAS.index(item[0])),
    )
    if not ranked or ranked[0][1] < 1:
        return {
            "area": UNCLASSIFIED_AREA,
            "confidence": 0,
            "evidence": {
                "method": "unclassified",
                "scores": {},
                "matches": [],
            },
        }

    area, top_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0
    total_score = sum(scores.values())
    share = top_score / total_score if total_score else 0
    margin = (top_score - second_score) / top_score if top_score else 0
    strength = min(top_score / 12, 1)
    confidence = round(
        min(0.99, (0.45 * share) + (0.35 * margin) + (0.20 * strength)),
        3,
    )
    winning_matches = sorted(
        matches[area], key=lambda item: item["points"], reverse=True
    )[:12]
    uses_provider_topic = any(
        match["signal"] in {"primary_provider_topic", "provider_topic"}
        for match in winning_matches
    )
    return {
        "area": area,
        "confidence": confidence,
        "evidence": {
            "method": (
                "provider_topic_plus_metadata"
                if uses_provider_topic
                else "metadata_heuristic"
            ),
            "scores": {
                name: round(score, 2)
                for name, score in ranked
                if score > 0
            },
            "matches": winning_matches,
        },
    }
