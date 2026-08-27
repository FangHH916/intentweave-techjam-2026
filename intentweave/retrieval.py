from __future__ import annotations

from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import re
import sqlite3


TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
PRICE_RE = re.compile(r"(?:\$|usd\s*)(\d+(?:\.\d+)?)", re.IGNORECASE)
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from",
    "i", "in", "is", "it", "me", "my", "of", "on", "or", "please", "some",
    "that", "the", "this", "to", "want", "with", "would", "you", "looking",
    "still", "exploring", "key", "requirement", "matters", "need", "actually",
    "ignore", "earlier", "preference", "what", "those", "options", "quite", "right",
    "yet", "about", "one", "specific", "additional", "use", "your", "judgment",
}

# A compact, auditable concept space supplies the semantic vector route without
# model downloads. Values are domain aliases; each text becomes a binary concept
# vector and is compared with cosine similarity.
CONCEPTS = {
    "footwear": ("shoe", "shoes", "sneaker", "sneakers", "footwear"),
    "boots": ("boot", "boots", "bootie", "booties"),
    "sandals": ("sandal", "sandals", "flip flop", "slides"),
    "tops": ("shirt", "shirts", "tee", "t-shirt", "top", "blouse"),
    "outerwear": ("jacket", "coat", "parka", "outerwear", "windbreaker"),
    "bottoms": ("pants", "trousers", "jeans", "leggings", "shorts", "joggers"),
    "dress": ("dress", "gown", "sundress"),
    "underwear": ("underwear", "briefs", "panties", "bra", "lingerie"),
    "bags": ("bag", "handbag", "purse", "wallet", "backpack", "crossbody"),
    "jewelry": ("jewelry", "necklace", "earrings", "bracelet", "ring", "pendant"),
    "athletic": ("running", "workout", "gym", "athletic", "sports", "training"),
    "outdoor": ("outdoor", "hiking", "trail", "camping", "waterproof"),
    "formal": ("formal", "business", "office", "wedding", "dressy"),
    "casual": ("casual", "everyday", "daily", "lounge"),
    "winter": ("winter", "warm", "thermal", "fleece", "insulated"),
    "sleep": ("sleep", "pajama", "pyjama", "nightgown", "robe"),
    "cotton": ("cotton",),
    "leather": ("leather", "suede"),
    "synthetic": ("polyester", "nylon", "spandex", "rayon", "lycra"),
    "lightweight": ("lightweight", "light weight", "breathable"),
    "comfort": ("comfortable", "comfort", "cushion", "padded", "soft"),
}


def text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return " ".join(f"{key} {item}" for key, item in value.items())
    if isinstance(value, list):
        return " ".join(str(item) for item in value)
    return str(value)


def terms(value: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(value) if len(token) > 1 and token.lower() not in STOPWORDS]


def raw_terms(value: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(value) if len(token) > 1]


def concept_vector(value: str) -> set[str]:
    lowered = value.casefold()
    tokens = set(raw_terms(lowered))
    result: set[str] = set()
    for concept, aliases in CONCEPTS.items():
        if any((alias in tokens) if " " not in alias else (alias in lowered) for alias in aliases):
            result.add(concept)
    return result


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def fts_quote(tokens: list[str]) -> str:
    return '"' + " ".join(token.replace('"', '') for token in tokens) + '"'


class HybridRetriever:
    """In-memory multi-route retrieval with local semantic-style reranking."""

    SEARCH_FIELDS = ("title", "categories", "features", "details", "store", "description")

    def __init__(self, catalog_path: str | Path) -> None:
        self.catalog_path = Path(catalog_path)
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self._build_index()

    def _build_index(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            "CREATE VIRTUAL TABLE products USING fts5("
            "parent_asin UNINDEXED, title, categories, features, details, store, description, "
            "price UNINDEXED, average_rating UNINDEXED, rating_number UNINDEXED, "
            "tokenize='unicode61 remove_diacritics 2')"
        )
        batch: list[tuple[str, ...]] = []
        with self.catalog_path.open(encoding="utf-8") as handle:
            for line in handle:
                product = json.loads(line)
                batch.append((
                    str(product["parent_asin"]), text(product.get("title")), text(product.get("categories")),
                    text(product.get("features")), text(product.get("details")), text(product.get("store")),
                    text(product.get("description")), "" if product.get("price") is None else str(product["price"]),
                    str(product.get("average_rating") or 0), str(product.get("rating_number") or 0),
                ))
                if len(batch) >= 1000:
                    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", batch)
                    batch.clear()
        if batch:
            cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", batch)
        self.connection.commit()

    def _route(self, expression: str, limit: int = 350) -> list[sqlite3.Row]:
        if not expression:
            return []
        try:
            return self.connection.execute(
                "SELECT *, bm25(products, 0.0, 7.0, 5.0, 2.7, 2.4, 2.0, 1.0, 0.0, 0.0, 0.0) AS lexical "
                "FROM products WHERE products MATCH ? ORDER BY lexical LIMIT ?",
                (expression, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            return []

    def search(
        self,
        messages: list[str],
        signals: list[str],
        constraints: list[str],
        goal: str,
        profile_terms: list[str],
        top_k: int,
    ) -> list[dict]:
        all_terms = unique(terms(" ".join(messages)))
        signal_terms = unique(terms(" ".join([goal, *constraints])))
        latest_terms = unique(terms(constraints[-1])) if constraints else unique(terms(goal))
        routes: list[tuple[float, list[sqlite3.Row]]] = []
        for index, constraint in enumerate(reversed(constraints[-6:])):
            phrase_tokens = raw_terms(constraint)[:55]
            if phrase_tokens:
                routes.append((3.4 - 0.25 * index, self._route(fts_quote(phrase_tokens), 250)))
        goal_terms = unique(terms(goal))
        if goal_terms:
            routes.append((2.4, self._route("categories : " + fts_quote(goal_terms), 350)))
            if signal_terms:
                constraint_or = " OR ".join(fts_quote([term]) for term in signal_terms[:45])
                combined = "categories : " + fts_quote(goal_terms) + " AND (" + constraint_or + ")"
                routes.append((4.0, self._route(combined, 450)))
        if latest_terms:
            routes.append((2.2, self._route(" OR ".join(fts_quote([term]) for term in latest_terms[:40]), 450)))
        if signal_terms:
            routes.append((1.8, self._route(" OR ".join(fts_quote([term]) for term in signal_terms[:60]), 500)))
        if all_terms:
            routes.append((1.0, self._route(" OR ".join(fts_quote([term]) for term in all_terms[:70]), 500)))

        query_concepts = concept_vector(" ".join([goal, *constraints]))
        if query_concepts:
            expanded = unique([
                alias
                for concept in sorted(query_concepts)
                for alias in CONCEPTS[concept]
                if " " not in alias
            ])
            semantic_expression = " OR ".join(fts_quote([alias]) for alias in expanded[:60])
            routes.append((0.5, self._route(semantic_expression, 450)))

        fused: dict[str, float] = defaultdict(float)
        rows: dict[str, sqlite3.Row] = {}
        for route_weight, route_rows in routes:
            for rank, row in enumerate(route_rows, start=1):
                asin = str(row["parent_asin"])
                rows[asin] = row
                fused[asin] += route_weight / (20.0 + rank)
        if not fused:
            return []

        query_counts = Counter(signal_terms or all_terms)
        latest_set = set(latest_terms)
        signal_phrases = [constraint.casefold() for constraint in constraints if len(terms(constraint)) >= 2]
        requested_price = self._requested_price(constraints)
        scored: list[tuple[float, str]] = []
        shortlist = sorted(fused.items(), key=lambda item: (-item[1], item[0]))[:220]
        for asin, fusion_score in shortlist:
            row = rows[asin]
            field_tokens = {
                "title": set(terms(row["title"])), "categories": set(terms(row["categories"])),
                "features": set(terms(row["features"])), "details": set(terms(row["details"])),
                "store": set(terms(row["store"])), "description": set(terms(row["description"])),
            }
            weighted_overlap = 0.0
            union_tokens = set().union(*field_tokens.values())
            for token in query_counts:
                best = 0.0
                for field, weight in (("title", 2.8), ("categories", 2.4), ("store", 2.0), ("features", 1.7), ("details", 1.5), ("description", 1.1)):
                    if token in field_tokens[field]:
                        best = max(best, weight)
                weighted_overlap += best * (1.25 if token in latest_set else 1.0)
            corpus = " ".join(str(row[field]) for field in self.SEARCH_FIELDS).casefold()
            document_concepts = concept_vector(corpus)
            concept_cosine = (
                len(query_concepts & document_concepts)
                / math.sqrt(len(query_concepts) * len(document_concepts))
                if query_concepts and document_concepts else 0.0
            )
            phrase_score = sum(8.0 + 0.15 * len(terms(phrase)) for phrase in signal_phrases if phrase in corpus)
            coverage_ratio = sum(1 for token in query_counts if token in union_tokens) / max(1, len(query_counts))
            price_score = self._price_score(requested_price, row["price"])
            rating = float(row["average_rating"] or 0)
            rating_count = float(row["rating_number"] or 0)
            quality_prior = max(0.0, rating - 3.5) * 0.05 + math.log1p(rating_count) * 0.008
            semantic_score = weighted_overlap / math.sqrt(max(1.0, len(query_counts)))
            final = (
                30.0 * fusion_score + semantic_score + 1.5 * concept_cosine
                + phrase_score + 2.0 * coverage_ratio + price_score + quality_prior
            )
            scored.append((final, asin))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [{"parent_asin": asin, "score": round(score, 6)} for score, asin in scored[:top_k]]

    @staticmethod
    def _requested_price(constraints: list[str]) -> float | None:
        for signal in reversed(constraints):
            match = PRICE_RE.search(signal)
            if match:
                return float(match.group(1))
        return None

    @staticmethod
    def _price_score(requested: float | None, raw_price: object) -> float:
        if requested is None or raw_price in (None, ""):
            return 0.0
        try:
            price = float(raw_price)
        except (TypeError, ValueError):
            return 0.0
        relative_error = abs(price - requested) / max(1.0, requested)
        return 7.0 * max(0.0, 1.0 - 4.0 * relative_error)
