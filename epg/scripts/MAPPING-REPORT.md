# EPG channel-id mapping — iptv-org → Online4Tech

**Generated:** 2026-11-27 (final run, run 5).
**Purpose:** the daily EPG generator grabs guides from bein.com, osn.com and
elcinema.com via the iptv-org grabber, then remaps every channel id to the
Online4Tech xmltv id used in the v2 EPG pack, so the guide data lands on the
same ids the channel files and EPGImport sources use.

## Summary

- **Union of iptv-org ids from the 3 sites: 187**
- **Mapped: 170 (91%)**
- **Unmatched: 17**
- **Ambiguous (mapped, but other plausible Online4Tech ids exist): 12**

| Site | Provided | Matched | Unmatched |
|---|---|---|---|
| bein.com | 50 | 46 | 4 |
| osn.com | 60 | 52 | 8 |
| elcinema.com | 104 | 99 | 5 |

The per-site counts add up to 197 matched site-ids because 27 iptv-org ids are
provided by more than one site (e.g. `DiscoveryChannelMiddleEastAfrica.us` by all
three) — the union is 187 unique ids.

## Sources

- **Our ids (Online4Tech):** v2 pack channels files
  `~/workspace/epg-research/online4tech-epg-pack/` —
  `o4t-epg-nilesat-ar.channels.xml`, `o4t-epg-nilesat-en.channels.xml`,
  `o4t-epg-allsats.channels.xml` — **2,020 unique xmltv ids**.
- **iptv-org data (fetched 2026-11-27, public):**
  `https://iptv-org.github.io/api/guides.json` (180,680 entries — which site
  provides which channel id) and `https://iptv-org.github.io/api/channels.json`
  (31,958 entries — id, name, alt_names, for matching).
- **Builder:** `build-mapping.py` in this folder (regenerates both files from the
  same inputs; intermediate state in `/tmp/mapping-state.json`).

## Method

Matching is by normalized name, with the site as a strong signal (a bein.com id
only ever maps to a beIN channel, never to an OSN one). Tiers, best match wins:

1. **Tier 0 — exact id:** iptv id with country suffix stripped equals an Online4Tech
   id with its suffix stripped (case-insensitive).
2. **Tier 1 — exact core key:** tokens of the iptv id (camelCase/digit split,
   qualifier tokens like premium/hd/fhd/uhd/4k/digital/english/french/arabic/afc/
   fta/sd/tv/channel/television dropped) equal the Online4Tech id's core key, or the
   iptv id's core equals an Online4Tech id's full key (country suffix allowed).
3. **Tier 2 — name / alt-names:** the channel's name or alt_names from channels.json
   (Arabic alt names that tokenize to a bare digit are ignored — they matched
   everything).
4. **Tier 3 — token subset, one direction only:** the Online4Tech id's tokens must be
   a subset of the iptv id's tokens (never the reverse), digit tokens must agree,
   and the smaller side must contain a non-digit token. A spin-off guard blocks the
   match when the iptv side carries an extra distinguishing token (arabia, originals,
   thaqafiya, drama, cinema, movies, series, kids, news, sports, music, …) — that
   means a different channel, not the base one.

**Overrides (61):** hand-checked choices where the automatic tier picked the wrong
twin — e.g. beIN Sports 2/3 → `beIN_SPORTS2_PREMIUM` / `beIN_SPORTS3_PREMIUM`,
OSN channels → plain `OSNtv …` ids, Alkass 1–8 → `Al-Kass-N`, RT.ru → `RT English`,
RTArabic.ru → `RT Arabic HD`, OnE.eg → `OnE.eg`, AlSaudiya.sa → `Saudiya_TV`,
AlNahar.eg → `AlNaharTV.eg`, OmanTV.om → `Oman TV General HD`, AlAoula.ma →
`Al Aoula inter`, AlShamsTV.eg → `Shams TV`, InvestigationDiscovery.uk → `Discovery ID`,
BloombergOriginals.us → `BloombergOriginalsAr.sa` (the Originals channel, distinct
from Bloomberg TV news).

**Excludes (never matched):** ids whose apparent twin is a different channel —
CNNArabic.ae (no CNN Arabic id; `CNN` is English), FoxArabia.ae (no Fox Arabia id;
`FOX-HD` is English Fox), FoxLifeMiddleEast.ae (no Fox Life id), MBCMood.sa (no MBC
Mood id; `MBC` is MBC 1), AlarabiyaPortrait.ae (no Portrait feed id), ATV.kw (no Adala
TV id; `ATV Kurd` is Kurdish), SaudiThaqafiyaTV.sa (no Thaqafiya/Culture id; `Saudi TV`
is the main channel).

**Rules followed:** no id was invented — every key exists in guides.json for one of the
three sites and every value exists in the v2 pack. One-to-one: each iptv-org id maps
to exactly one Online4Tech id, and no two iptv-org ids share a target. Anything
without a confident match is listed as unmatched below, not guessed.

## Matched list

Tier: 0 = exact id · 1 = exact core key · 2 = name/alt-names · 3 = token subset ·
override = hand-checked. Ids provided by several sites appear under each of them.

### bein.com (46/50 matched)

| iptv-org id | Online4Tech xmltv id | tier |
|---|---|---|
| `AlJazeeraDocumentary.qa` | `Al Jazeera Documentary` | override |
| `AlkassEight.qa` | `Al-Kass-8` | override |
| `AlkassFive.qa` | `Al-Kass-5` | override |
| `AlkassFour.qa` | `Al-Kass-4` | override |
| `AlkassOne.qa` | `Al-Kass-1-1` | override |
| `AlkassSeven.qa` | `Al-Kass-7` | override |
| `AlkassSix.qa` | `Al-Kass-6` | override |
| `AlkassThree.qa` | `Al-Kass-3` | override |
| `AlkassTwo.qa` | `Al-Kass-2` | override |
| `BeJunior.qa` | `beJUNIOR` | 0 |
| `BloombergTV.us` | `Bloomberg` | 1 |
| `CBeebiesMiddleEast.uk` | `CBeebies` | 3 |
| `ClubMTVEurope.uk` | `Mtv-club` | 3 |
| `DiscoveryChannelMiddleEastAfrica.us` | `DiscoveryChannelMiddleEastAfrica.us` | 0 |
| `EuronewsEnglish.fr` | `Euronews HD.ua` | 1 |
| `Fatafeat.ae` | `Fatafeat` | override |
| `FoodNetworkEMEA.us` | `food-network` | 3 |
| `FoxActionMoviesMENA.hk` | `Fox-Action-Movies` | 3 |
| `FoxMoviesMiddleEast.us` | `FOX Movies TV` | 3 |
| `HGTVArabia.us` | `HGTVAr.sa` | 1 |
| `JeemTV.qa` | `Jeem-HD-01` | override |
| `MTV80s.uk` | `Mtv-80s` | 1 |
| `MTV90s.uk` | `Mtv-90s` | 1 |
| `StarMoviesMiddleEast.ae` | `StarMoviesMiddleEast.hk` | 0 |
| `StarWorldMiddleEast.ae` | `StarWorldMiddleEast.hk` | 0 |
| `beINGourmet.qa` | `beIN GOURMET` | override |
| `beINMovies1Premiere.qa` | `beIN 1 PREM` | override |
| `beINMovies2Action.qa` | `Bein_Movies_Action_2` | override |
| `beINMovies3Drama.qa` | `beIN 3 PREM` | override |
| `beINMovies4Family.qa` | `Bein_Movies_Family_4` | override |
| `beINSeries1.qa` | `BeInSeriesHD1.eg` | override |
| `beINSports2.qa` | `beIN_SPORTS2_PREMIUM` | override |
| `beINSports3.qa` | `beIN_SPORTS3_PREMIUM` | override |
| `beINSports4.qa` | `beIN SPORTS 4` | 1 |
| `beINSports4KHDR.qa` | `beIN 4K` | override |
| `beINSports5.qa` | `beINSPORTS5.qa` | 0 |
| `beINSports6.qa` | `beINSPORTS6.qa` | 0 |
| `beINSports7.qa` | `beIN SPORTS 7` | 1 |
| `beINSports8.qa` | `beIN SPORTS 8` | 1 |
| `beINSports9.qa` | `beINSPORTS9.qa` | 0 |
| `beINSportsMax1.qa` | `beIN_SPORTS_MAX1` | override |
| `beINSportsMax2.qa` | `beIN_SPORTS_MAX2` | override |
| `beINSportsMax3.qa` | `beIN_SPORTS_MAX3` | override |
| `beINSportsMax4.qa` | `beIN_SPORTS_MAX4` | override |
| `beINSportsMax5.qa` | `beIN SPORTS MAX 5` | 1 |
| `beINSportsMax6.qa` | `beINSPORTSMAX6.qa` | 0 |

### osn.com (52/60 matched)

| iptv-org id | Online4Tech xmltv id | tier |
|---|---|---|
| `AbuDhabiSports1.ae` | `AD_Sports_1` | 2 |
| `AbuDhabiTV.ae` | `AbuDhabi_TV` | override |
| `AlArabyTV.qa` | `AL ARABY TV` | 1 |
| `AlArabyTV2.qa` | `AlArabyTV2.uk` | 0 |
| `AlHadath.sa` | `AL HADATH HD` | 1 |
| `AlQuranAlKareemTV.sa` | `Al Quran` | 3 |
| `AlraiTV.kw` | `AlraiTV.kw` | 0 |
| `AnimalPlanetEurope.uk` | `Animal Planet Europe` | 1 |
| `BBCArabic.uk` | `BBC Arabic` | 1 |
| `BahrainTV.bh` | `BahrainTV` | 0 |
| `BloombergOriginals.us` | `BloombergOriginalsAr.sa` | override |
| `BloombergTV.us` | `Bloomberg` | 1 |
| `CNNInternational.us` | `CNN International HD.ua` | 1 |
| `CartoonNetworkArabic.ae` | `CartoonNetworkArabic.ae` | 0 |
| `CartoonNetworkMENA.uk` | `Cartoon Network HD` | override |
| `DMC.eg` | `dmc` | override |
| `DiscoveryChannelMiddleEastAfrica.us` | `DiscoveryChannelMiddleEastAfrica.us` | 0 |
| `DubaiTV.ae` | `DubaiTV.ae` | 0 |
| `Fatafeat.ae` | `Fatafeat` | override |
| `GINXTV.uk` | `GINX` | 2 |
| `Gametoon.nl` | `Gametoon` | 0 |
| `HistoryMiddleEast.us` | `History HD` | 3 |
| `InvestigationDiscovery.uk` | `Discovery ID` | override |
| `KSASports1.sa` | `KSA SPORTS 1` | 1 |
| `MBC1.ae` | `MBC 1` | override |
| `MBC3.ae` | `MBC 3` | override |
| `MBC5.ae` | `MBC5.ae` | 0 |
| `MBCDrama.ae` | `MBC Drama` | override |
| `MBCIraq.iq` | `MBC IRAQ` | override |
| `MBCMasr.eg` | `MBC Masr` | override |
| `MBCMasr2.eg` | `MBC Masr 2` | override |
| `MBCPlusDrama.sa` | `MBC+Drama` | override |
| `MoonbugKids.uk` | `Moonbug Kids` | 1 |
| `NickJrArabia.ae` | `NickJrAr.sa` | 1 |
| `NickelodeonArabia.ae` | `NickelodeonAr.sa` | 1 |
| `NicktoonsArabia.ae` | `NickToonsAr.sa` | 1 |
| `OSNComedy.ae` | `OSNtv Comedy` | override |
| `OSNKids.ae` | `OSNtv Kids` | override |
| `OSNMezze.ae` | `OSNtv Mezze` | override |
| `OSNMoviesAction.ae` | `OSNtv Movies Action` | override |
| `OSNMoviesHollywood.ae` | `OSNtv Movies Hollywood` | override |
| `OSNMoviesPremiere.ae` | `OSNtv Movies Premiere` | override |
| `OSNShowcase.ae` | `OSNtv Showcase` | override |
| `OSNYahala.ae` | `OSNtv Yahala` | override |
| `OSNYahalaAflam.ae` | `OSNtv Yahala Aflam` | override |
| `OSNYahalaBilArabi.ae` | `OSNtv Yahala Bil Arabi` | override |
| `OmanTV.om` | `Oman TV General HD` | override |
| `RT.ru` | `RT English` | override |
| `RTArabic.ru` | `RT Arabic HD` | override |
| `RoyaTV.jo` | `ROYA HD` | 1 |
| `SkyNewsArabia.ae` | `Sky News Arabia` | 1 |
| `TLCArabia.us` | `TLCAr.sa` | 1 |

### elcinema.com (99/104 matched)

| iptv-org id | Online4Tech xmltv id | tier |
|---|---|---|
| `2MMonde.ma` | `2MMonde.ma` | 0 |
| `AbuDhabiTV.ae` | `AbuDhabi_TV` | override |
| `AlAoula.ma` | `Al Aoula inter` | override |
| `AlArabyTV2.qa` | `AlArabyTV2.uk` | 0 |
| `AlDafrahTV.ae` | `AlDafrahTV.ae` | 0 |
| `AlIraqia.iq` | `Iraqia` | 1 |
| `AlJadeed.lb` | `AlJadeed.lb` | 0 |
| `AlKaheraWalNas.eg` | `AlKaheraWalNas.eg` | 0 |
| `AlKaheraWalNas2.eg` | `AlKaheraWalNas2.eg` | 0 |
| `AlMasriyah.eg` | `AlMasriyah.eg` | 0 |
| `AlNahar.eg` | `AlNaharTV.eg` | override |
| `AlNaharDrama.eg` | `AlNaharDrama.eg` | 0 |
| `AlRasheedTV.iq` | `AlRasheedTV.iq` | 0 |
| `AlSaeedah.eg` | `AlSaeedah` | 0 |
| `AlSaudiya.sa` | `Saudiya_TV` | override |
| `AlShamsTV.eg` | `Shams TV` | override |
| `AlSharqiyaMinKabla.ae` | `AlSharqiyaMinKabla.ae` | 0 |
| `AlhayatTV.eg` | `AlhayatTV.eg` | 0 |
| `Alsumaria.iq` | `Alsumaria.iq` | 0 |
| `Althania.sy` | `Althania.eg` | 0 |
| `AmmanTV.jo` | `AmmanTV.jo` | 0 |
| `BahrainTV.bh` | `BahrainTV` | 0 |
| `CBC.eg` | `CBC.eg` | 0 |
| `CBCDrama.eg` | `CBCDrama.eg` | 0 |
| `CBCSofra.eg` | `CBCSofra.eg` | 0 |
| `CartoonNetworkArabic.ae` | `CartoonNetworkArabic.ae` | 0 |
| `Cima.eg` | `Cima` | 0 |
| `DMC.eg` | `dmc` | override |
| `DMCDrama.eg` | `DMC_Drama` | override |
| `DijlahTV.iq` | `DijlahTV.eg` | 0 |
| `DiscoveryChannelMiddleEastAfrica.us` | `DiscoveryChannelMiddleEastAfrica.us` | 0 |
| `DubaiOne.ae` | `DubaiOne` | 0 |
| `DubaiTV.ae` | `DubaiTV.ae` | 0 |
| `DubaiZaman.ae` | `DubaiZaman.ae` | 0 |
| `ERTU1.eg` | `AL Oula HD` | 2 |
| `EchoroukTV.dz` | `EchoroukTV.eg` | 0 |
| `EgyptianTV.eg` | `EgyptianTV.eg` | 0 |
| `ElMehwarChannel.eg` | `ElMehwarChannel.eg` | 0 |
| `ElWatania1.tn` | `Watania1` | 1 |
| `ElWatania2.tn` | `Watania2` | 1 |
| `FoxActionMoviesMENA.hk` | `Fox-Action-Movies` | 3 |
| `FujairahTV.ae` | `Fujairah` | 1 |
| `HadhramautTV.ye` | `HadhramautTV.eg` | 0 |
| `JordanTV.jo` | `JordanTV` | 0 |
| `LBC.sa` | `LBC` | 0 |
| `LBCInternational.lb` | `LBCInternational.lb` | 0 |
| `LanaTV.lb` | `LanaTV.lb` | 0 |
| `MBC1.ae` | `MBC 1` | override |
| `MBC2.ae` | `MBC 2` | override |
| `MBC3.ae` | `MBC 3` | override |
| `MBC4.ae` | `MBC 4` | override |
| `MBC5.ae` | `MBC5.ae` | 0 |
| `MBCAction.ae` | `MBC Action` | override |
| `MBCBollywood.ae` | `MBC Bollywood` | override |
| `MBCDrama.ae` | `MBC Drama` | override |
| `MBCIraq.iq` | `MBC IRAQ` | override |
| `MBCMasr.eg` | `MBC Masr` | override |
| `MBCMasr2.eg` | `MBC Masr 2` | override |
| `MBCMasrDrama.sa` | `MBCMasrDrama.eg` | 0 |
| `MBCMax.ae` | `MBCMAX.eg` | 0 |
| `MBCPlusDrama.sa` | `MBC+Drama` | override |
| `MTV.lb` | `MTV.eg` | 0 |
| `MasperoZaman.eg` | `MasperoZaman.eg` | 0 |
| `MixBelAraby.eg` | `MixBelAraby.eg` | 0 |
| `NationalGeographicAbuDhabi.ae` | `NationalGeographicAbuDhabi.ae` | 0 |
| `NessmaElJadida.tn` | `Nessma.tn` | 2 |
| `NileDrama.eg` | `NileDrama.eg` | 0 |
| `NileLife.eg` | `NileLife.eg` | 0 |
| `OmanTV.om` | `Oman TV General HD` | override |
| `OnDrama.eg` | `OnDrama.eg` | 0 |
| `OnE.eg` | `OnE.eg` | override |
| `QatarTelevision.qa` | `Qatar TV HD` | 1 |
| `RotanaCinemaEgypt.eg` | `Rotana Cinema Masr.eg` | 2 |
| `RotanaCinemaKSA.sa` | `RotanaCinemaKSA.sa` | 0 |
| `RotanaClassic.sa` | `RotanaClassic.sa` | 0 |
| `RotanaComedy.sa` | `Rotana_Comedy` | 1 |
| `RotanaDrama.sa` | `RotanaDrama.sa` | 0 |
| `RotanaKhalijia.sa` | `RotanaKhalijia.sa` | 0 |
| `RoyaTV.jo` | `ROYA HD` | 1 |
| `SBC.sa` | `SBC` | 0 |
| `SadaElbalad.eg` | `SadaElbalad.eg` | 0 |
| `SadaElbalad2.eg` | `SadaElbalad2.eg` | 0 |
| `SadaElbaladDrama.eg` | `SadaElbaladDrama.eg` | 0 |
| `SalamTV.ly` | `SalamTV` | 0 |
| `SamaDubai.ae` | `SamaDubai.ae` | 0 |
| `SharjahTV.ae` | `SharjahTV.ae` | 0 |
| `StarMoviesMiddleEast.ae` | `StarMoviesMiddleEast.hk` | 0 |
| `StarWorldMiddleEast.ae` | `StarWorldMiddleEast.hk` | 0 |
| `TeN.eg` | `Ten.eg` | 0 |
| `ThikrayatTV.sa` | `ThikrayatTV.sa` | 0 |
| `UTV.iq` | `UTV.iq` | 0 |
| `ZeeAlwan.ae` | `ZeeAlwan.eg` | 0 |
| `beINDrama1.qa` | `beINDrama.eg` | override |
| `beINMovies1Premiere.qa` | `beIN 1 PREM` | override |
| `beINMovies2Action.qa` | `Bein_Movies_Action_2` | override |
| `beINMovies3Drama.qa` | `beIN 3 PREM` | override |
| `beINSeries1.qa` | `BeInSeriesHD1.eg` | override |
| `beINSeries2.qa` | `beINSeriesHD2.eg` | override |
| `iFilmArabic.ir` | `iFilmArabic.ir` | 0 |

## Unmatched list

These 17 ids have no confident Online4Tech target. The EPG generator drops them
(they simply get no guide data) — it does not guess.

| iptv-org id | iptv name | Reason |
|---|---|---|
| `ATV.kw` | ATV | no Adala TV id in the pack; 'ATV Kurd' is a Kurdish channel |
| `AlManar.lb` | Al-Manar | no candidate in Online4Tech pack |
| `AlarabiyaPortrait.ae` | Alarabiya Portrait | no Portrait feed id in the pack; 'Alarabiya.ae' is the main Al Arabiya feed (Portrait likely simulcasts it — needs confirmation) |
| `Baraem.qa` | Baraem | no candidate in Online4Tech pack |
| `CNNArabic.ae` | CNN Arabic | no CNN Arabic id in the pack; 'CNN' is the English channel |
| `CrimePlusInvestigation.us` | Crime + Investigation | no candidate in Online4Tech pack |
| `FoxArabia.ae` | Fox Arabia | no Fox Arabia id in the pack; 'FOX-HD' is the English Fox channel (likely twin 'Fox Be Elaraby TV' needs confirmation) |
| `FoxLifeMiddleEast.ae` | Fox Life Middle East | no Fox Life id in the pack; 'FOX-HD' is the main Fox channel |
| `History2MiddleEast.us` | History 2 Middle East | no candidate in Online4Tech pack |
| `KTV1.kw` | KTV 1 | no candidate in Online4Tech pack |
| `MBCMood.sa` | MBC Mood | no MBC Mood id in the pack; 'MBC' is the main MBC 1 channel |
| `MCMTop.fr` | MCM Top | no candidate in Online4Tech pack |
| `Masah.sa` | Masah | no candidate in Online4Tech pack |
| `MotorvisionPlus.de` | Motorvision+ | no candidate in Online4Tech pack |
| `NationalGeographicMiddleEast.uk` | National Geographic Middle East | no candidate in Online4Tech pack |
| `RFMTV.fr` | RFM TV | no candidate in Online4Tech pack |
| `SaudiThaqafiyaTV.sa` | Saudi Thaqafiya TV | no Thaqafiya/Culture id in the pack; 'Saudi TV' is the main Saudi channel |

Notes on the unmatched:

- **Baraem.qa** (bein.com), **KTV1.kw**, **AlManar.lb**, **Masah.sa**,
  **MCMTop.fr**, **MotorvisionPlus.de**, **CrimePlusInvestigation.us**,
  **History2MiddleEast.us**, **NationalGeographicMiddleEast.uk** — no id for these
  channels exists anywhere in the v2 pack (2,020 ids checked). They can only be
  covered if the channel file / pack gains them.
- **FoxArabia.ae** — the pack has a likely twin, `Fox Be Elaraby TV`, which was NOT
  used because it is not certain to be the same feed as Fox Arabia — needs
  confirmation before mapping.
- **AlarabiyaPortrait.ae** — no Portrait feed id; the main `Alarabiya.ae` feed is
  mapped, and Portrait most likely simulcasts it — needs confirmation.
- **RFMTV.fr** — the pack has `RFMTVAr.sa` (the Arabic feed); the French RFM TV feed
  is not the same channel, so it was left unmatched rather than attached to the
  Arabic feed.
- **CNNArabic.ae / MBCMood.sa / FoxLifeMiddleEast.ae / ATV.kw /**
  **SaudiThaqafiyaTV.sa** — see Excludes above; each has a look-alike id in the pack
  that is a different channel.

## Ambiguous cases (mapped, alternates exist)

All 12 are same-channel twins (SD/HD, case, or satellite variants of one channel),
not different channels. The chosen id is the main Nilesat feed where one could be
identified; the alternates are recorded so the choice can be revisited.

| iptv-org id | Chosen | Alternates | Note |
|---|---|---|---|
| `AlArabyTV.qa` | `AL ARABY TV` | `AL ARABY TV HD`, `Al Araby HD.ar` | chosen is the main feed; HD twin is a different SID |
| `AlHadath.sa` | `AL HADATH HD` | `Al Hadath`, `Al_Hadath`, `Al Hadath HD.ua` | chosen is the HD feed |
| `AlQuranAlKareemTV.sa` | `Al Quran` | `Al-Quran TV`, `Al Quran TV.ar` | tier-3 subset match; all three are the same channel |
| `BBCArabic.uk` | `BBC Arabic` | `BBC_Arabic`, `BBC Arabic.ua` | chosen carries the Nilesat ref; alternates are Arabsat/Hotbird twins |
| `ERTU1.eg` | `AL Oula HD` | `AL oula` | chosen is the HD feed |
| `FujairahTV.ae` | `Fujairah` | `Fujairah TV HD`, `Fujairah.eg` | same channel, SD/HD twins |
| `KSASports1.sa` | `KSA SPORTS 1` | `KSA Sports +1`, `KSA Sports 1 HD.ua`, `KSA sports 1.ar` | chosen is the main feed — NOT `KSA Sports +1` (a different channel) |
| `RotanaCinemaEgypt.eg` | `Rotana Cinema Masr.eg` | `RotanaCinemaMasr.eg`, `Rotana Cinema Masr.ps` | chosen is the HD feed; alternates are SD / other-sat twins |
| `RoyaTV.jo` | `ROYA HD` | `Roya`, `Roya TV HD.ua`, `Roya.eg` | chosen is the HD feed |
| `SkyNewsArabia.ae` | `Sky News Arabia` | `Sky News Arabia HD`, `Sky_News_Arabia_HD`, `Sky News Arabia HD.ua` | same channel, SD/HD twins |
| `beINSports4.qa` | `beIN SPORTS 4` | `beIN SPORTS 4 AFC`, `beIN_SPORTS4`, `beIN SPORTS 4 AFC.qa`, `beIN SPORTS 4.qa` | `beIN SPORTS 4 AFC` is a different channel (AFC feed); the other two are same-channel twins |
| `beINSports7.qa` | `beIN SPORTS 7` | `beIN_SPORTS7`, `beIN SPORTS 7.qa` | same-channel twins |

## Low-confidence flags (mapped — worth a second look)

- **`MBCMax.ae` → `MBCMAX.eg`** (tier 0, exact id stem) — channels.json has no name
  for this id, and MBC Max is a defunct brand, so the id may be stale. Kept because
  the id stem matches exactly.
- **`MTV.lb` → `MTV.eg`** (tier 0, exact id stem) — channels.json has no name for this
  id; `MTV.eg` is assumed to be MTV Lebanon (not the music MTV).
- **`EuronewsEnglish.fr` → `Euronews HD.ua`** — there is only one Euronews id in the
  pack, so it is the only possible target; it is not verified to be the English feed.
- **`AlQuranAlKareemTV.sa` → `Al Quran`** — tier-3 subset match (the weakest tier);
  the two other Al-Quran ids are the same channel, so the risk is only which twin.

## The big gap: beIN Sports 1

**`beINSports1.qa` (beIN Sports 1) is NOT provided by bein.com, osn.com or
elcinema.com in guides.json** — it is provided by other sites, including
**beinsports.com** (beIN's own site), canalplus, orange and others. The generator
cannot cover beIN Sports 1 until a 4th grabber site is added; check beinsports.com's
grabber status (in the iptv-org/epg repo) before adding it. All other beIN Sports
channels (2–9, Max 1–6, 4K) and beIN Movies/Series/Drama/Gourmet are mapped.

## Validation

- All 170 targets exist in the v2 pack channels files (checked).
- No two iptv-org ids share a target (checked).
- All 170 keys are ids that guides.json attributes to at least one of the three sites
  (checked).
- End-to-end test with `remap-epg-ids.py` on a synthetic bein.com guide:
  `beINSports2.qa` → `beIN_SPORTS2_PREMIUM`, `beINSports5.qa` → `beINSPORTS5.qa`,
  `AlkassOne.qa` → `Al-Kass-1-1`; unmatched `Baraem.qa` and its programmes dropped.

