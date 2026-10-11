import pytest

from apps.catalog.tests.factories import ProductFactory
from apps.content.models import FaqItem, Page

pytestmark = pytest.mark.django_db


def test_unpublished_drafts_are_hidden(client):
    # Миграция создаёт черновики страниц и FAQ — они не видны на сайте
    assert Page.objects.filter(slug="delivery").exists()
    assert client.get("/api/v1/content/pages").json() == []
    assert client.get("/api/v1/content/pages/delivery").status_code == 404
    assert client.get("/api/v1/content/faq").json() == []


def test_page_html_is_sanitized(client):
    Page.objects.create(
        slug="about-us",
        title="About",
        is_published=True,
        content_en=(
            "<h2>Hello</h2><script>alert(1)</script>"
            '<p onclick="steal()">Text <a href="javascript:alert(1)">bad</a> '
            '<a href="https://maison.uz">good</a></p><img src=x onerror=alert(1)>'
        ),
    )

    html = client.get("/api/v1/content/pages/about-us").json()["content"]

    assert "<h2>Hello</h2>" in html
    assert "script" not in html and "onclick" not in html and "onerror" not in html
    assert "javascript:" not in html
    assert 'href="https://maison.uz"' in html and 'rel="noopener noreferrer"' in html


def test_published_pages_and_translations(client):
    Page.objects.filter(slug="delivery").update(is_published=True)

    pages = client.get("/api/v1/content/pages", headers={"accept-language": "ru"}).json()

    assert pages == [
        {"slug": "delivery", "title": "Доставка и оплата", "footer_group": "customers"}
    ]
    detail = client.get("/api/v1/content/pages/delivery", headers={"accept-language": "uz"}).json()
    assert "BTS" in detail["content"]


def test_faq(client):
    FaqItem.objects.update(is_published=True)
    FaqItem.objects.create(question_en="Q?", answer_en="<p>A</p><script>x</script>", position=99)

    faq = client.get("/api/v1/content/faq").json()

    assert len(faq) == 5
    assert faq[-1]["answer"] == "<p>A</p>"


def test_sitemap(client):
    ProductFactory(slug="visible")
    ProductFactory(slug="draft", is_published=False)
    Page.objects.filter(slug="about").update(is_published=True)

    data = client.get("/api/v1/content/sitemap").json()

    assert [p["slug"] for p in data["products"]] == ["visible"]
    assert len(data["brands"]) == 1
    assert [p["slug"] for p in data["pages"]] == ["about"]
