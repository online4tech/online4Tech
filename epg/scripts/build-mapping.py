#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build iptv-org id -> Online4Tech xmltv id mapping for the daily EPG
generator (sites: bein.com, osn.com, elcinema.com).

Method (generic first, explicit overrides only where the generic
matcher gets it wrong — every override is logged with a reason):
  0. Exact id match (country suffix stripped, case-insensitive).
  1. Core-key match: tokenize both ids (camelCase split, digit split,
     number words -> digits), drop qualifier tokens
     (premium/hd/fhd/uhd/4k/digital/english/french/arabic/afc/fta/sd),
     alias prem -> premiere. Compare core keys.
  2. Name match: same core-key comparison using the iptv channel name
     and alt_names from channels.json.
  3. Token-subset match (only if exactly one O4T id qualifies).
Ranking of candidates: plain id (no country suffix) first; then
exact-tier over core-key over name over subset; then closest full
normalized form (edit distance); then id string (deterministic).
Ambiguity: top-2 candidates with equal rank -> flagged, first picked.
Never invent an id: unmatched ids are listed, not guessed.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

PACK_DIR = "/home/hatch/workspace/epg-research/online4tech-epg-pack"
GEN_DIR = "/home/hatch/workspace/epg-research/epg-generator"
SITES = ["bein.com", "osn.com", "elcinema.com"]

QUALIFIERS = {"premium", "hd", "fhd", "uhd", "4k", "digital",
              "english", "french", "arabic", "afc", "fta", "sd",
              "tv", "channel", "television"}
NUMWORDS = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
            "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
            "eleven": "11", "twelve": "12"}
ALIASES = {"prem": "premiere", "ar": "arabia"}
COMPOUNDS = {"nicktoons": ["nick", "toons"]}
# Tier-3 subset guard: if the iptv side has an extra token from this
# set that the O4T candidate lacks, the candidate is a DIFFERENT
# channel (a spin-off), not the base channel — block the match.
# Region words (middle/east/mena/emea/europe) and proper-name words
# (kareem) are NOT in this set, so legitimate feed matches still pass.
TIER3_BLOCK = {"arabia", "arabic", "originals", "thaqafiya", "culture",
               "life", "mood", "portrait", "drama", "cinema", "movies",
               "movie", "series", "kids", "kid", "news", "sports",
               "sport", "documentary", "music", "comedy", "action",
               "family", "crime", "history", "science", "food",
               "plus", "max", "xtra"}
COUNTRY_SUFFIX = re.compile(r"\.[a-z]{2}$", re.I)


def strip_country(i):
    return COUNTRY_SUFFIX.sub("", i)


def tokenize(s):
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s)
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", s)
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    toks = []
    for t in s.split():
        parts = re.split(r"(?<=[a-z])(?=\d)|(?<=\d)(?=[a-z])", t)
        toks.extend(p for p in parts if p)
    # merge "be" + "in" -> "bein"
    merged = []
    i = 0
    while i < len(toks):
        if toks[i] == "be" and i + 1 < len(toks) and toks[i + 1] == "in":
            merged.append("bein")
            i += 2
        else:
            merged.append(toks[i])
            i += 1
    out = []
    for t in merged:
        t = NUMWORDS.get(t, t)
        t = ALIASES.get(t, t)
        if t in COMPOUNDS:
            out.extend(COMPOUNDS[t])
        else:
            out.append(t)
    return out


def core_key(tokens):
    # drop qualifier tokens and a leading Arabic article (al/el) —
    # "Al Watania 1" and "Watania 1" are the same channel.
    toks = [t for t in tokens if t not in QUALIFIERS]
    if toks and toks[0] in ("al", "el"):
        toks = toks[1:]
    return " ".join(toks)


def full_key(tokens):
    return " ".join(tokens)


def lev(a, b):
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if abs(la - lb) > 6:
        return 99
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * lb
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1,
                         prev[j - 1] + (0 if ca == cb else 1))
        prev = cur
    return prev[lb]


def main():
    # ---- Online4Tech ids ----
    o4t_files = defaultdict(set)   # id -> pack files it appears in
    o4t_refs = defaultdict(set)    # id -> service refs
    for fname in ["o4t-epg-nilesat-ar.channels.xml",
                  "o4t-epg-nilesat-en.channels.xml",
                  "o4t-epg-allsats.channels.xml"]:
        root = ET.parse("%s/%s" % (PACK_DIR, fname)).getroot()
        for ch in root.findall("channel"):
            cid = ch.get("id")
            o4t_files[cid].add(fname)
            if ch.text:
                o4t_refs[cid].add(ch.text.strip())
    o4t_ids = sorted(o4t_files)
    print("O4T unique ids: %d" % len(o4t_ids))

    # index O4T ids by exact-stripped form and by core key
    by_exact = defaultdict(list)
    by_core = defaultdict(list)
    by_full = defaultdict(list)
    for cid in o4t_ids:
        toks = tokenize(strip_country(cid))
        by_exact[strip_country(cid).lower()].append(cid)
        by_core[core_key(toks)].append(cid)
        by_full[full_key(toks)].append(cid)

    # ---- iptv-org data ----
    guides = json.load(open("/tmp/iptv-guides.json"))
    channels = {c["id"]: c for c in json.load(open("/tmp/iptv-channels.json"))}
    site_ids = {}
    for site in SITES:
        ids = sorted({r["channel"] for r in guides
                      if r["site"] == site and r.get("channel")})
        site_ids[site] = ids
        print("%s: %d unique ids" % (site, len(ids)))
    all_iptv = sorted(set().union(*[set(v) for v in site_ids.values()]))
    print("union iptv ids: %d" % len(all_iptv))

    # which sites provide each iptv id
    id_sites = defaultdict(list)
    for site in SITES:
        for i in site_ids[site]:
            id_sites[i].append(site)

    # ---- exclusions: ids that must NOT be matched even though a
    # same-name twin exists (the twin is a different channel) ----
    EXCLUDES = {
        "CNNArabic.ae": "no CNN Arabic id in the pack; 'CNN' is the English channel",
        # Same-name twins that are different channels (the generic
        # subset matcher would wrongly attach them to the base channel).
        "FoxArabia.ae": "no Fox Arabia id in the pack; 'FOX-HD' is the English Fox channel (likely twin 'Fox Be Elaraby TV' needs confirmation)",
        "FoxLifeMiddleEast.ae": "no Fox Life id in the pack; 'FOX-HD' is the main Fox channel",
        "MBCMood.sa": "no MBC Mood id in the pack; 'MBC' is the main MBC 1 channel",
        "AlarabiyaPortrait.ae": "no Portrait feed id in the pack; 'Alarabiya.ae' is the main Al Arabiya feed (Portrait likely simulcasts it — needs confirmation)",
        "ATV.kw": "no Adala TV id in the pack; 'ATV Kurd' is a Kurdish channel",
        "SaudiThaqafiyaTV.sa": "no Thaqafiya/Culture id in the pack; 'Saudi TV' is the main Saudi channel",
    }

    # ---- match ----
    mapping = {}
    ambiguous = {}   # iptv id -> (chosen, [alternates], tier)
    unmatched = {}   # iptv id -> reason
    match_info = {}  # iptv id -> (tier, chosen, candidates)

    def rank(cands, iid, iptv_toks):
        """Rank candidate O4T ids. Returns ordered list.
        Order: exact case-sensitive id match, plain id (no country
        suffix), country suffix matching the iptv id's suffix, token
        overlap with the iptv id (more is better), token symmetric
        difference (less is better), id string (deterministic)."""
        iptv_suffix = COUNTRY_SUFFIX.search(iid)
        iptv_suffix = iptv_suffix.group(0).lower() if iptv_suffix else ""
        icore = set(t for t in iptv_toks if t not in QUALIFIERS)

        def score(cid):
            exact_case = 0 if strip_country(cid) == strip_country(iid) else 1
            plain = 0 if not COUNTRY_SUFFIX.search(cid) else 1
            csuf = COUNTRY_SUFFIX.search(cid)
            suffix_match = 0 if (csuf and csuf.group(0).lower() == iptv_suffix
                                and iptv_suffix) else 1
            oc = set(t for t in tokenize(strip_country(cid))
                     if t not in QUALIFIERS)
            overlap = len(icore & oc)
            symdiff = len(icore ^ oc)
            return (exact_case, plain, suffix_match, -overlap, symdiff, cid)
        return sorted(cands, key=score)

    for iid in all_iptv:
        if iid in EXCLUDES:
            unmatched[iid] = EXCLUDES[iid]
            continue
        toks = tokenize(strip_country(iid))
        cands = {}  # cid -> best tier (0 exact, 1 core, 2 name, 3 subset)
        # tier 0: exact stripped id
        for cid in by_exact.get(strip_country(iid).lower(), []):
            cands[cid] = min(cands.get(cid, 99), 0)
        # tier 1: core key of the id itself
        for cid in by_core.get(core_key(toks), []):
            cands[cid] = min(cands.get(cid, 99), 1)
        # tier 2: name / alt_names core keys. Skip a name whose core
        # tokens are all digits (or empty): a non-Latin alt name such
        # as "أبو ظبي الرياضية 1" tokenizes to just "1" and would
        # otherwise match every id whose core is "1" (ONE, One TV...).
        ch = channels.get(iid, {})
        names = [ch.get("name", "")] + list(ch.get("alt_names") or [])
        for name in names:
            if not name:
                continue
            ntoks = tokenize(name)
            core_toks = [t for t in ntoks if t not in QUALIFIERS]
            if not any(not t.isdigit() for t in core_toks):
                continue
            for cid in by_core.get(core_key(ntoks), []):
                cands[cid] = min(cands.get(cid, 99), 2)
            for cid in by_full.get(full_key(ntoks), []):
                cands[cid] = min(cands.get(cid, 99), 2)
        # tier 3: token-subset — ONLY the O4T side's tokens subset of
        # the iptv side's (the target must not add meaningful tokens
        # the query lacks: "ATV" must never match "ATV Kurd"). Two
        # guards: (a) digit tokens must agree (a "History 2" must
        # never match a "History 1"); (b) the smaller side must
        # contain a non-digit token (a lone number token like "ONE"
        # must never match a real channel).
        if not cands:
            itoks = set(t for t in toks if t not in QUALIFIERS)
            idigits = {t for t in itoks if t.isdigit()}
            hits = []
            for cid in o4t_ids:
                otoks = set(t for t in tokenize(strip_country(cid))
                            if t not in QUALIFIERS)
                odigits = {t for t in otoks if t.isdigit()}
                if idigits != odigits:
                    continue
                if not any(not t.isdigit() for t in otoks):
                    continue
                if itoks and otoks and otoks <= itoks:
                    # Spin-off guard: an extra distinguishing token on
                    # the iptv side means a different channel.
                    if (itoks - otoks) & TIER3_BLOCK:
                        continue
                    hits.append(cid)
            if len(hits) == 1:
                cands[hits[0]] = 3
            elif len(hits) > 1:
                # keep them as weak candidates for the ambiguous list
                for h in hits:
                    cands[h] = 3
        if not cands:
            unmatched[iid] = "no candidate in Online4Tech pack"
            continue
        # rank: best tier first, then exact-case / plain / suffix /
        # overlap / symdiff / id
        best_tier = min(cands.values())
        top = [cid for cid, t in cands.items() if t == best_tier]
        ordered = rank(top, iid, toks)
        chosen = ordered[0]
        mapping[iid] = chosen
        match_info[iid] = (best_tier, chosen, ordered)
        if len(ordered) > 1:
            # ambiguous if the runner-up ties on the rank key minus id
            def rkey(cid):
                exact_case = 0 if strip_country(cid) == strip_country(iid) else 1
                plain = 0 if not COUNTRY_SUFFIX.search(cid) else 1
                csuf = COUNTRY_SUFFIX.search(cid)
                isuf = COUNTRY_SUFFIX.search(iid)
                suffix_match = 0 if (csuf and isuf and
                                    csuf.group(0).lower() == isuf.group(0).lower()) else 1
                icore = set(t for t in toks if t not in QUALIFIERS)
                oc = set(t for t in tokenize(strip_country(cid))
                         if t not in QUALIFIERS)
                return (exact_case, plain, suffix_match,
                        -len(icore & oc), len(icore ^ oc))
            if rkey(ordered[0]) == rkey(ordered[1]):
                ambiguous[iid] = (chosen, ordered[1:], best_tier)

    # ---- overrides: canonical choices where the generic matcher picks
    # a non-canonical twin (same channel, several O4T ids). Each entry:
    # iptv id -> (chosen O4T id, reason). Only ids that exist on both
    # sides are used; anything else is ignored with a warning.
    overrides = {
        # beIN Sports N: the _PREMIUM ids are the canonical Nilesat
        # package ids (brief: prefer plain/canonical). NOTE: _PREMIUM
        # ids exist in the pack only for Sports 1-3; for 4-9 the plain
        # "beIN SPORTS N" ids are the canonical ones (generic match).
        "beINSports2.qa": ("beIN_SPORTS2_PREMIUM", "canonical beIN premium id"),
        "beINSports3.qa": ("beIN_SPORTS3_PREMIUM", "canonical beIN premium id"),
        "beINSportsMax1.qa": ("beIN_SPORTS_MAX1", "plain canonical max id"),
        "beINSportsMax2.qa": ("beIN_SPORTS_MAX2", "plain canonical max id"),
        "beINSportsMax3.qa": ("beIN_SPORTS_MAX3", "plain canonical max id"),
        "beINSportsMax4.qa": ("beIN_SPORTS_MAX4", "plain canonical max id"),
        "beINSports4KHDR.qa": ("beIN 4K", "plain canonical 4K id"),
        # beIN Movies: plain short forms, consistent 1/2/3 pattern.
        "beINMovies1Premiere.qa": ("beIN 1 PREM", "plain movies-1 id"),
        "beINMovies2Action.qa": ("Bein_Movies_Action_2", "plain movies-2 action id"),
        "beINMovies3Drama.qa": ("beIN 3 PREM", "plain movies-3 id (pattern with 1/2)"),
        "beINMovies4Family.qa": ("Bein_Movies_Family_4", "plain movies-4 family id"),
        "beINSeries1.qa": ("BeInSeriesHD1.eg", "only series-1 id in pack"),
        "beINSeries2.qa": ("beINSeriesHD2.eg", "only series-2 id in pack"),
        "beINDrama1.qa": ("beINDrama.eg", "only drama id in pack"),
        "beINGourmet.qa": ("beIN GOURMET", "plain gourmet id"),
        # OSN: the plain "OSNtv ..." ids are the canonical package ids.
        "OSNComedy.ae": ("OSNtv Comedy", "plain canonical OSN id"),
        "OSNKids.ae": ("OSNtv Kids", "plain canonical OSN id"),
        "OSNMezze.ae": ("OSNtv Mezze", "plain canonical OSN id"),
        "OSNMoviesAction.ae": ("OSNtv Movies Action", "plain canonical OSN id"),
        "OSNMoviesHollywood.ae": ("OSNtv Movies Hollywood", "plain canonical OSN id"),
        "OSNMoviesPremiere.ae": ("OSNtv Movies Premiere", "plain canonical OSN id"),
        "OSNShowcase.ae": ("OSNtv Showcase", "plain canonical OSN id"),
        "OSNYahala.ae": ("OSNtv Yahala", "plain canonical OSN id"),
        "OSNYahalaAflam.ae": ("OSNtv Yahala Aflam", "plain canonical OSN id"),
        "OSNYahalaBilArabi.ae": ("OSNtv Yahala Bil Arabi", "plain canonical OSN id"),
        # Alkass: the "Al-Kass-N" forms (with dedup -1 where present).
        "AlkassOne.qa": ("Al-Kass-1-1", "numbered Alkass id"),
        "AlkassTwo.qa": ("Al-Kass-2", "numbered Alkass id"),
        "AlkassThree.qa": ("Al-Kass-3", "numbered Alkass id"),
        "AlkassFour.qa": ("Al-Kass-4", "numbered Alkass id"),
        "AlkassFive.qa": ("Al-Kass-5", "numbered Alkass id"),
        "AlkassSix.qa": ("Al-Kass-6", "numbered Alkass id"),
        "AlkassSeven.qa": ("Al-Kass-7", "numbered Alkass id"),
        "AlkassEight.qa": ("Al-Kass-8", "numbered Alkass id"),
        # General: plain display-name ids over suffixed twins.
        "AlJazeeraDocumentary.qa": ("Al Jazeera Documentary", "plain canonical id"),
        "AbuDhabiTV.ae": ("AbuDhabi_TV", "plain canonical id"),
        "DMC.eg": ("dmc", "plain id (lowercase twin)"),
        "DMCDrama.eg": ("DMC_Drama", "plain id"),
        "Fatafeat.ae": ("Fatafeat", "plain id"),
        "MBC1.ae": ("MBC 1", "plain canonical id"),
        "MBC2.ae": ("MBC 2", "plain canonical id"),
        "MBC3.ae": ("MBC 3", "plain canonical id"),
        "MBC4.ae": ("MBC 4", "plain canonical id"),
        "MBCAction.ae": ("MBC Action", "plain canonical id"),
        "MBCBollywood.ae": ("MBC Bollywood", "plain canonical id"),
        "MBCDrama.ae": ("MBC Drama", "plain canonical id"),
        "MBCIraq.iq": ("MBC IRAQ", "plain canonical id"),
        "MBCMasr.eg": ("MBC Masr", "plain canonical id"),
        "MBCMasr2.eg": ("MBC Masr 2", "plain canonical id"),
        "MBCPlusDrama.sa": ("MBC+Drama", "plain canonical id"),
        "JeemTV.qa": ("Jeem-HD-01", "only Jeem id in pack"),
        # Generic matcher failures fixed by hand (verified against the
        # pack contents): RT English vs Arabic are different channels
        # (qualifier-stripping merged them); "ONE" is a different
        # channel from OnE/KTV1/ElWatania1; Al Saudiya is Saudi TV 1;
        # Cartoon Network MENA is the English feed, Arabic is separate.
        # Ref-checked picks: Al-Nahar main feed, Oman TV general feed,
        # Al Aoula Nilesat feed, Al Shams HD feed.
        "RT.ru": ("RT English", "RT English feed (not Arabic)"),
        "RTArabic.ru": ("RT Arabic HD", "RT Arabic feed, HD id"),
        "OnE.eg": ("OnE.eg", "Egyptian ON E (exact id, not the ONE channel)"),
        "AlSaudiya.sa": ("Saudiya_TV", "Saudi TV 1"),
        "CartoonNetworkMENA.uk": ("Cartoon Network HD", "MENA English feed; Arabic is a separate channel"),
        "AlNahar.eg": ("AlNaharTV.eg", "main Al-Nahar feed (same service ref as Al-Nahar One)"),
        "OmanTV.om": ("Oman TV General HD", "main Oman TV feed (Culture/Sport are different channels)"),
        "AlAoula.ma": ("Al Aoula inter", "Nilesat feed, ref C8A (International id has non-sat refs)"),
        "AlShamsTV.eg": ("Shams TV", "HD feed, clean Nilesat ref (SHAMS TV id has a non-standard namespace)"),
        # ID is Investigation Discovery's brand.
        "InvestigationDiscovery.uk": ("Discovery ID", "ID = Investigation Discovery"),
        # Bloomberg Originals is a distinct channel from Bloomberg TV
        # (news); the only Originals id in the pack is the Ar one.
        "BloombergOriginals.us": ("BloombergOriginalsAr.sa", "the Originals channel (distinct from Bloomberg TV news)"),
    }
    applied = []
    for iid, (target, reason) in sorted(overrides.items()):
        if iid not in all_iptv:
            print("override skipped (not provided): %s" % iid)
            continue
        if target not in o4t_files:
            print("override skipped (target not in pack): %s -> %s" % (iid, target))
            continue
        if iid in unmatched:
            del unmatched[iid]
        prev = mapping.get(iid)
        mapping[iid] = target
        match_info[iid] = ("override", target, [target])
        ambiguous.pop(iid, None)
        applied.append((iid, prev, target, reason))

    # ---- write outputs ----
    with open("%s/id-mapping.json" % GEN_DIR, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")

    state = {
        "mapping": mapping,
        "ambiguous": {k: {"chosen": v[0], "alternates": v[1], "tier": v[2]}
                      for k, v in ambiguous.items()},
        "unmatched": unmatched,
        "match_info": {k: {"tier": v[0], "chosen": v[1], "candidates": v[2]}
                       for k, v in match_info.items()},
        "overrides_applied": applied,
        "site_ids": site_ids,
        "id_sites": dict(id_sites),
        "channels": channels,
        "o4t_files": {k: sorted(v) for k, v in o4t_files.items()},
        "o4t_refs": {k: sorted(v) for k, v in o4t_refs.items()},
        "all_iptv": all_iptv,
    }
    with open("/tmp/mapping-state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False)

    print("mapped: %d / %d" % (len(mapping), len(all_iptv)))
    print("ambiguous: %d" % len(ambiguous))
    print("unmatched: %d" % len(unmatched))
    print("overrides applied: %d" % len(applied))
    print("\nUNMATCHED:")
    for iid in sorted(unmatched):
        ch = channels.get(iid, {})
        print("  %s | %s | %s" % (iid, ch.get("name", "?"), unmatched[iid]))
    print("\nAMBIGUOUS:")
    for iid in sorted(ambiguous):
        chosen, alts, tier = ambiguous[iid]
        print("  %s -> %s | alternates: %s | tier %s"
              % (iid, chosen, alts, tier))


if __name__ == "__main__":
    main()
