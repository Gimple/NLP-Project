import re
from typing import Dict, Set

LEGIT_PATTERNS = {
    # Global
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk", "nytimes.com", "ft.com", "financialtimes.com",
    "theguardian.com", "cnn.com", "bloomberg.com", "wsj.com", "scmp.com", "asia.nikkei.com", "time.com",
    "afp.com", "channelnewsasia.com", "news.sky.com", "sky.com", "nhk.or.jp", "dw.com", "voanews.com",
    "npr.org", "cbc.ca", "abc.net.au", "straitstimes.com", "smh.com.au", "independent.co.uk",
    "economist.com", "washingtonpost.com", "politico.com", "aa.com.tr", "arabnews.com",
    "indiatoday.in", "thehindu.com", "timesofindia.indiatimes.com", "indiatimes.com",
    "jakartapost.com", "bangkokpost.com", "thestar.com.my", "khaleejtimes.com", "asiaone.com",
    "heraldsun.com.au", "dailymail.co.uk", "nzherald.co.nz", "aljazeera.com",
    # Philippines
    "inquirer.net", "gmanetwork.com", "abs-cbn.com", "news.abs-cbn.com", "philstar.com",
    "manilabulletin.com", "mb.com.ph", "bworldonline.com", "rappler.com", "sunstar.com.ph",
    "pna.gov.ph", "tribune.net.ph", "manilatimes.net", "malaya.com.ph", "boholchronicle.com.ph",
    "mindanaotimes.com.ph", "visayandailystar.com", "cebudailynews.inquirer.net", "mindanaodailynews.com",
}

FAKE_PATTERNS = {
    "thepeoplesvoice.tv", "newspunch.com", "clickhole.com", "dcgazette.com", "infowars.com",
    "worldnewsdailyreport.com", "yournewswire.com", "dailybuzzlive.com", "nationalreport.net",
    "huzlers.com", "adobochronicles.com", "tahonews.com", "socialnewsph.com", "pinoyviralnews.net",
    "24sevendailynews.com", "360newslive.com", "aboutdu30.com", "adobochronicles.com",
    "aksyon.tv", "theoion.com", "allthingspinoy.com", "angatpilipino.com",
    "asianpolicypress.com", "asensopinoy.com", "astigtayopinoy.com", "balitaonline.com.ph",
    "balitangcitizenph.com", "balitangpanglahat.com", "balitangpinoy.com", "blogdidu30.com",
    "netcitizen.ph", "news8bureau.com", "newscenterph.com", "newsfeedsociety.com",
    "newsglobal.com.ph", "newsinfolearn.com", "newsmediaph.com", "newspaper.ph",
    "newstitans.com", "clickhole.com", "newzflash.com", "newsbite.top",
    "onlinebalita.com", "philippinechronicle.com", "pinoyviralnews.net", "socialnewsph.com",
    "tahonews.com", "dcgazette.com", "infowars.com", "worldnewsdailyreport.com",
    "yournewswire.com", "dailybuzzlive.com", "nationalreport.net", "huzlers.com"
}

# # Tabloid-but-generally-credible: smaller positive boost
# TABLOID_PATTERNS = {"dailymail.co.uk"}

CREDIBLE_BOOST = 500.0   
FAKE_BOOST = 500.0      
TABLOID_BOOST = 250.0    # Bump


def _normalize_source(source: str) -> str:
    if not source:
        return ""
    s = source.strip().lower()
    # keep only hostname part if someone passed a full URL by mistake
    s = re.sub(r"^https?://", "", s)
    s = s.split("/")[0]
    if s.startswith("www."):
        s = s[4:]
    return s


def _matches_any(host: str, patterns: Set[str]) -> bool:
    # match if exact, subdomain of pattern, or contains token uniquely
    for p in patterns:
        if host == p or host.endswith("." + p) or p in host:
            return True
    return False


def compute_prior_boosts(source: str) -> Dict[str, float]:

    host = _normalize_source(source)
    if not host:
        return {"real": 0.0, "fake": 0.0}

    # # Tabloid mild boost first
    # if _matches_any(host, TABLOID_PATTERNS):
    #     return {"real": TABLOID_BOOST, "fake": 0.0}

    # Strong credible or fake source
    if _matches_any(host, LEGIT_PATTERNS):
        return {"real": CREDIBLE_BOOST, "fake": 0.0}
    if _matches_any(host, FAKE_PATTERNS):
        return {"real": 0.0, "fake": FAKE_BOOST}

    # Unknown source: no boost
    return {"real": 0.0, "fake": 0.0}
