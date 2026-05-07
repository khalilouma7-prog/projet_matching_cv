import scrapy
from datetime import date

class RekruteSpider(scrapy.Spider):
    name = "rekrute"
    allowed_domains = ["rekrute.com"]
    start_urls = ["https://www.rekrute.com/offres-emploi-maroc.html"]
    
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
    }

    def parse(self, response):
        # Chaque offre est dans li.post-id
        offers = response.css("li.post-id")
        for offer in offers:
            url = offer.css("a.titreJob::attr(href)").get()
            if url:
                if not url.startswith("http"):
                    url = "https://www.rekrute.com" + url
                yield response.follow(url, callback=self.parse_offer)

        # Pagination
        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_offer(self, response):
        # Titre
        title = response.css("div.listWrpService h1::text").get("").strip()
        
        # Company
        company = response.css("h2.h2italic a::text").get("") or \
                  response.css("h2.h2italic::text").get("")
        company = company.strip()
        
        # Description — tous les paragraphes dans div.col-md-12.blc
        description = " ".join(
            response.css("div.col-md-12.blc p::text").getall()
        ).strip()
        
        # Skills — liste featureInfo
        skills = response.css("ul.featureInfo li::text").getall()
        skills = [s.strip() for s in skills if s.strip()]
        
        # Infos supplémentaires
        experience = response.css("ul.featureInfo li::text").get("").strip()
        contract = ""
        for li in response.css("ul.featureInfo li::text").getall():
            if "CDI" in li or "CDD" in li or "Stage" in li or "Freelance" in li:
                contract = li.strip()
                break

        location = response.css(
            "div.listWrpService span.location::text"
        ).get("").strip()
        if not location:
            # fallback — chercher dans le titre de la page
            location = response.css("title::text").get("").split("-")[-1].strip()

        yield {
            "title":        title,
            "company":      company,
            "location":     location,
            "contract":     contract or "Autre",
            "experience":   experience,
            "description":  description,
            "skills":       skills[:10],
            "url":          response.url,
            "source":       "rekrute",
            "published_at": date.today().isoformat(),
        }