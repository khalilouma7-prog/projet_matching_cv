# backend/scraping/spiders/emploima_spider.py
import scrapy
from datetime import date


class EmploiMaSpider(scrapy.Spider):
    """Spider pour Emploi.ma."""
    name            = "emploima"
    allowed_domains = ["emploi.ma"]
    start_urls      = ["https://www.emploi.ma/recherche-jobs-maroc"]    

    custom_settings = {
        "DOWNLOAD_DELAY":          2,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
        ),
    }

    def parse(self, response):
        for link in response.css("h2.job-title a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_offer)

        next_page = response.css("a[rel='next']::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_offer(self, response):
        yield {
            "title":       response.css("h1.job-title::text").get("").strip(),
            "company":     response.css("div.company-name::text").get("").strip(),
            "sector":      response.css("span.sector::text").get("").strip(),
            "location":    response.css("span.job-location::text").get("").strip(),
            "contract":    response.css("span.job-type::text").get("Autre").strip(),
            "experience":  response.css("span.experience::text").get("").strip(),
            "description": " ".join(response.css("div.job-description *::text").getall()),
            "skills":      response.css("li.skill::text").getall(),
            "url":         response.url,
            "source":      "emploima",
            "published_at": date.today().isoformat(),
        }
