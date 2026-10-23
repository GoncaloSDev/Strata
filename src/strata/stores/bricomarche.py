"""Bricomarché (bricomarche.pt): WooCommerce Store API, um preço por loja física (variações)."""

from strata.models import Found

NAME = "Bricomarché"
BASE = "https://www.bricomarche.pt"
SEARCH_URL = BASE + "/wp-json/wc/store/v1/products"


def parent_key(p):
    return None


def cheapest(rows):
    return None


def has_stock(row) -> bool:
    return True


def store_link(row):
    return "", ""


def offer_from(parent, rows):
    return None


async def search(query: str, fetch) -> Found:
    return Found(offers=[], raw=0)
