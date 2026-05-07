# backend/scraping/spiders/indeed_spider.py
import scrapy
from datetime import date


class IndeedSpider(scrapy.Spider):
    """Spider pour Indeed Maroc — utilise Selenium pour le JS."""
    name            = "indeed"
    allowed_domains = ["ma.indeed.com"]
    start_urls      = ["https://ma.indeed.com/jobs?q=data&l=Maroc"]

    custom_settings = {
        "DOWNLOAD_DELAY":           3,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        # Activer le middleware Selenium si nécessaire :
        # "DOWNLOADER_MIDDLEWARES": {
        #     "apps.scraping.middlewares.SeleniumMiddleware": 800,
        # },
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
        ),
    }

    def parse(self, response):
        for card in response.css("div.job_seen_beacon"):
            link = card.css("h2.jobTitle a::attr(href)").get()
            if link:
                yield response.follow(
                    f"https://ma.indeed.com{link}",
                    callback=self.parse_offer,
                )

        next_page = response.css("a[data-testid='pagination-page-next']::attr(href)").get()
        if next_page:
            yield response.follow(
                f"https://ma.indeed.com{next_page}",
                callback=self.parse,
            )

    def parse_offer(self, response):
        yield {
            "title":       response.css("h1.jobsearch-JobInfoHeader-title::text").get("").strip(),
            "company":     response.css("div[data-company-name]::text").get("").strip(),
            "location":    response.css("div[data-testid='job-location']::text").get("").strip(),
            "contract":    response.css("span[data-testid='job-type-label']::text").get("Autre").strip(),
            "description": " ".join(response.css("div#jobDescriptionText *::text").getall()),
            "skills":      [],   # Indeed ne liste pas les skills explicitement
            "url":         response.url,
            "source":      "indeed",
            "published_at": date.today().isoformat(),
        }
