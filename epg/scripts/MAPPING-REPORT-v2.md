# EPG id-mapping v2 — report

Date: 2026-11-27. Builder: `/tmp/build-mapping-v2.py` (kept in /tmp; only `id-mapping.json` + this report live in the generator dir).

## Result

- **Total entries: 213** (v1: 170, all preserved unchanged; **v2 added: 43**).
- Grabber output ids covered: **213 / 284 (75%)**.

| site | output ids | mapped | v1 | v2 new | coverage |
|---|---|---|---|---|---|
| bein.com | 76 | 58 | 46 | 12 | 76% |
| osn.com | 80 | 66 | 52 | 14 | 82% |
| elcinema.com | 105 | 101 | 99 | 2 | 96% |
| beinsports.com | 63 | 28 | 13 | 15 | 44% |
| **union** | **284** | **213** | **170** | **43** | **75%** |

## Why v2 was needed

v1 was built from the iptv-org API (`guides.json`), but the grabber outputs ids from its own per-site channels files, which differ in three ways:
1. **@-suffixes** — the grabber's `xmltv_id` carries a feed suffix (`@SD`, `@MENA`, `@USA`); the output id is the part before `@` (the remap script now strips it).
2. **Empty xmltv_id → site_id** — verified in `grab.ts`: a channel with an empty `xmltv_id` outputs its `site_id`. All osn.com ids are site_ids (numbers like `204`); bein.com rows use `sports#N` / `entertainment#N`; beinsports.com rows with no xmltv_id output their UUID.
3. **beinsports.com was never mapped** — v1 had no beinsports.com ids at all; that site is the only source of **beIN Sports 1** (the other three sites do not provide it).

## Method (same as v1, plus v2 deltas)

- Distinct grabber output ids per site: bein 76, osn 80, elcinema 105, beinsports 63 — union 284.
- Matching: normalized names (4 tiers — exact id, core key with qualifier tokens dropped, name/alt-names from `channels.json`, one-direction token subset), site as a strong signal (a bein.com id maps to a beIN channel, never an OSN one).
- v2 changes: **"afc" removed from the qualifier list** (AFC feeds are distinct channels — beIN SPORTS 1 AFC ≠ beIN SPORTS 1); the tier-3 block extended with language/region + feed tokens; word-segmentation for all-caps slugs (`beINSPORTSXTRA3` → bein/sports/xtra/3, `beINJUNIOR` → bein/junior); overrides apply only to keys missing from v1.
- **Region-aware one-feed-per-channel guard** (replaces v1's blunt guard, which dropped BOTH feeds for XTRA 3–9): each row's region is recorded at parse time (bein/osn/elcinema = MENA; beinsports.com = region from the filename). For each pack id: a v1 key claiming it stands (every new key claiming it is dropped); otherwise exactly ONE new key is kept, by priority base id > MENA site row (bein/osn/elcinema) > MENA beinsports UUID; if no MENA feed exists for the id, ALL its keys are dropped (a non-MENA schedule does not belong on the MENA channel). No v1 entry is ever removed. Verified: no pack id is claimed by 2+ new keys.
- Overrides (new keys only, 3): `beINSports1.qa` → `beIN_SPORTS1_PREMIUM` (same canonical premium id as Sports 2/3 in v1), `sports#1` → `beIN_SPORTS1_PREMIUM` (same feed, dropped by the guard in favour of the base id), `entertainment#23` → `beJUNIOR` (dropped by the guard — v1 `BeJunior.qa` stands).

## Key wins

- **beIN Sports 1 is now mapped** — `beINSports1.qa` → `beIN_SPORTS1_PREMIUM` (the Nilesat premium feed, same as Sports 2/3 in v1). The MENA beinsports UUID feed `7836FEA9-…` maps to the plain `beIN SPORTS 1` pack id — a different service ref (different transponder), so both stay: each ref gets its own EPG.
- **beIN SPORTS XTRA 3–9 now covered** — via the bein.com rows `sports#19–25` (no `beINSportsXtra3–9.qa` base ids exist anywhere in the grabber files; the MENA UUIDs for the same channels were dropped by the guard as duplicate feeds).
- **OSN site_ids resolved** — `204` → `OSNtv One` (the empty-xmltv_id case), plus 13 more OSN numbers (`208` Showcase Classics, `225` Movies Horror, `307` Crime, `4502` Now, `5666` Movies Family, `5669` Movies Comedy, `5672` Pop Up, `6607/6610/6612/6613` eClutch, `CrimePlusInvestigation.us` → `C I`, `History2MiddleEast.us` → `H2 HD`).
- **AFC feeds mapped to AFC ids** — `beINSportsAFC{,1,2,3}.qa` → `beIN SPORTS {,1,2,3} AFC`, plus the MENA UUIDs for AFC 4/5/6 and beIN SPORTS 9.
- **beIN SPORTS 1/2 EN + FR** — `sports#12–15` → `beIN SPORTS 1/2 EN/FR.qa` (no base ids exist for the EN/FR feeds, so the bein.com rows are the only feed).
- **elcinema.com now 96%** — only `1135` → `Emirates` and `KTV1.kw` → `KuwaitTV.kw` were missing.

## Added entries (43)

### bein.com (+12)

- `sports#12` → `beIN SPORTS 1 EN.qa`
- `sports#13` → `beIN SPORTS 2 EN.qa`
- `sports#14` → `beIN SPORTS 1 FR.qa`
- `sports#15` → `beIN SPORTS 2 FR.qa`
- `sports#18` → `beIN SPORTS XTRA 2`
- `sports#19` → `beIN SPORTS XTRA 3`
- `sports#20` → `beINSPORTSXTRA4.qa`
- `sports#21` → `beINSPORTSXTRA5.qa`
- `sports#22` → `beINSPORTSXTRA6.qa`
- `sports#23` → `beINSPORTSXTRA7.qa`
- `sports#24` → `beINSPORTSXTRA8.qa`
- `sports#25` → `beINSPORTSXTRA9.qa`

### osn.com (+14)

- `204` → `OSNtv One`
- `208` → `OSNtv Showcase Classics`
- `225` → `OSNtv Movies Horror`
- `307` → `OSNtv Crime`
- `4502` → `OSNtv Now`
- `5666` → `OSNtv Movies Family`
- `5669` → `OSNtv Movies Comedy`
- `5672` → `OSNtv POP UP`
- `6607` → `eClutchAccess.sa`
- `6610` → `eClutch Live`
- `6612` → `eClutchLIVE2.sa`
- `6613` → `eClutchArabic.sa`
- `CrimePlusInvestigation.us` → `C I`
- `History2MiddleEast.us` → `H2 HD`

### elcinema.com (+2)

- `1135` → `Emirates`
- `KTV1.kw` → `KuwaitTV.kw`

### beinsports.com (+15)

- `2BF668DF-1B76-4199-88CE-8691FD86AD8C` → `beIN SPORTS 6 AFC`
- `42680C3C-580F-43DA-BDD8-02651BD10F32` → `beIN SPORTS 4 AFC`
- `5C08D9D3-C713-4F1F-947E-87C761428B9B` → `beIN SPORTS 9`
- `7836FEA9-6B39-4A1A-8352-DC5FCB97A16C` → `beIN SPORTS 1`
- `B0DBD19A-9F44-4197-BD09-2B6A5F315F3B` → `beIN SPORTS 5 AFC`
- `beINSports.qa` → `beIN SPORTS`
- `beINSports1.qa` → `beIN_SPORTS1_PREMIUM`
- `beINSportsAFC.qa` → `beIN SPORTS AFC`
- `beINSportsAFC1.qa` → `beIN SPORTS 1 AFC`
- `beINSportsAFC2.qa` → `beIN SPORTS 2 AFC`
- `beINSportsAFC3.qa` → `beIN SPORTS 3 AFC`
- `beINSportsNBA.qa` → `beIN SPORTS NBA.qa`
- `beINSportsNews.qa` → `beIN SPORTS NEWS`
- `beINSportsXtra1.qa` → `beIN SPORTS XTRA 1`
- `beINSportsXtra2.qa` → `beINSPORTSXTRA2.qa`

## Ambiguous (6, best pick kept — alternates listed)

- `5672` → `OSNtv POP UP` (alternates: `OSNtv Pop up`, `OSNtvPopUp.sa`; tier 2)
- `7836FEA9-6B39-4A1A-8352-DC5FCB97A16C` → `beIN SPORTS 1` (alternates: `beIN_SPORTS1`, `beIN_SPORTS1_ENGLISH`, `beIN_SPORTS1_FRENCH`, `beIN_SPORTS1_PREMIUM`, `beIN SPORTS 1.qa`; tier 2)
- `beINSports.qa` → `beIN SPORTS` (alternates: `beIN Sports`, `bein_SPORTS_FTA`, `beIN SPORTS.qa`; tier 1)
- `beINSportsNews.qa` → `beIN SPORTS NEWS` (alternates: `beIN Sports News`, `beIN SPORTS NEWS.qa`; tier 1)
- `beINSportsXtra1.qa` → `beIN SPORTS XTRA 1` (alternates: `beIN_SPORTS_XTRA1`, `beIN SPORTS XTRA 1.qa`, `beINSPORTSXTRA1Digital.qa`; tier 1)
- `sports#18` → `beIN SPORTS XTRA 2` (alternates: `beIN_SPORTS_XTRA2`, `beIN SPORTS XTRA 2.qa`, `beINSPORTSXTRA2.qa`; tier 2)

Notes: `5672` → `OSNtv POP UP` is a case-variant twin choice (`OSNtv Pop up` / `OSNtvPopUp.sa` are the same channel spelled differently — harmless). `7836FEA9-…` → `beIN SPORTS 1` vs `beIN_SPORTS1_PREMIUM`: both are real pack ids with different service refs, so both stay (see Key wins). `beINSports.qa` → `beIN SPORTS` vs `beIN Sports` / `bein_SPORTS_FTA` / `beIN SPORTS.qa`: case/spelling twins of the same MENA main channel.

## Still unmatched (71)

### duplicate feed (guard dropped; kept feed named in reason) (16)

- `02821165-CA6E-4A60-B781-C9C67B587185` (beinsports.com — beIN SPORTS 1): duplicate MENA feed of 'beIN SPORTS 1'; kept 7836FEA9-6B39-4A1A-8352-DC5FCB97A16C
- `1752F091-A114-4629-BED4-46E0BB488A24` (beinsports.com — beIN SPORTS XTRA 7): duplicate MENA feed of 'beINSPORTSXTRA7.qa'; kept sports#23
- `51D28C47-7B79-4007-81A3-BFDF9BC65A3B` (beinsports.com — beIN SPORTS XTRA 5): duplicate MENA feed of 'beINSPORTSXTRA5.qa'; kept sports#21
- `522050CE-EBD3-43EA-B636-42B034FDC05C` (beinsports.com — beIN SPORTS XTRA 9): duplicate MENA feed of 'beINSPORTSXTRA9.qa'; kept sports#25
- `7A8040D9-7BAF-477E-B9F7-8BAB88F677E8` (beinsports.com — beIN SPORTS XTRA 4): duplicate MENA feed of 'beINSPORTSXTRA4.qa'; kept sports#20
- `9ABD32F9-C6D9-4DD5-B936-2C7E6546292E` (beinsports.com — beIN SPORTS XTRA 6): duplicate MENA feed of 'beINSPORTSXTRA6.qa'; kept sports#22
- `A31EDF08-2A80-4D1F-9016-43A9C6138255` (beinsports.com — beIN SPORTS): duplicate MENA feed of 'beIN SPORTS'; kept beINSports.qa
- `A4320E60-381D-4435-8294-B4F3F33BF01C` (beinsports.com — beIN SPORTS 1): duplicate MENA feed of 'beIN SPORTS 1'; kept 7836FEA9-6B39-4A1A-8352-DC5FCB97A16C
- `B76EB90E-0657-4D61-9265-68ADA92E34CD` (beinsports.com — beIN SPORTS): duplicate MENA feed of 'beIN SPORTS'; kept beINSports.qa
- `CD634732-20D1-4137-94E7-939DE93D056D` (beinsports.com — beIN SPORTS XTRA 8): duplicate MENA feed of 'beINSPORTSXTRA8.qa'; kept sports#24
- `CDF1A4C8-26DD-4C33-A239-F729A3B09295` (beinsports.com — beIN SPORTS XTRA 3): duplicate MENA feed of 'beIN SPORTS XTRA 3'; kept sports#19
- `E227320A-8BA4-4ECB-A521-6DA53ADED441` (beinsports.com — beIN SPORTS 1): duplicate MENA feed of 'beIN SPORTS 1'; kept 7836FEA9-6B39-4A1A-8352-DC5FCB97A16C
- `sports#1` (bein.com — beINSPORTS1): duplicate MENA feed of 'beIN_SPORTS1_PREMIUM'; kept beINSports1.qa
- `sports#10` (bein.com — beINSPORTSNews): duplicate MENA feed of 'beIN SPORTS NEWS'; kept beINSportsNews.qa
- `sports#11` (bein.com — beINSPORTS): duplicate MENA feed of 'beIN SPORTS'; kept beINSports.qa
- `sports#17` (bein.com — beINSPORTSXTRA1): duplicate MENA feed of 'beIN SPORTS XTRA 1'; kept beINSportsXtra1.qa

### non-MENA feeds only (no MENA schedule for this channel) (6)

- `07C1C284-D784-4AD2-9F7E-022DCD196D04` (beinsports.com — beIN SPORTS 3): non-MENA feeds only for 'beIN SPORTS 3' — schedule does not belong on the MENA channel
- `5F323488-6662-42DC-BE1C-B954ECDD5CD7` (beinsports.com — beIN SPORTS 2): non-MENA feeds only for 'beIN SPORTS 2' — schedule does not belong on the MENA channel
- `7C714598-E7ED-4B0F-8BD1-E8E80D473922` (beinsports.com — beIN SPORTS 3): non-MENA feeds only for 'beIN SPORTS 3' — schedule does not belong on the MENA channel
- `DDFC8C16-6363-4A2C-AE66-2CE357DBC28E` (beinsports.com — beIN SPORTS 2): non-MENA feeds only for 'beIN SPORTS 2' — schedule does not belong on the MENA channel
- `E41B16D3-5172-4D56-B2C7-E2BB41E38CAD` (beinsports.com — beIN SPORTS 3): non-MENA feeds only for 'beIN SPORTS 3' — schedule does not belong on the MENA channel
- `F3CE2580-D815-4D33-84FC-6B95742BFB00` (beinsports.com — beIN SPORTS 3): non-MENA feeds only for 'beIN SPORTS 3' — schedule does not belong on the MENA channel

### already covered by a v1 entry (6)

- `beIN4K.qa` (beinsports.com — beIN 4K): channel already covered by v1 beINSports4KHDR.qa
- `entertainment#10` (bein.com — beINSERIES2): channel already covered by v1 beINSeries2.qa
- `entertainment#11` (bein.com — beINDRAMA): channel already covered by v1 beINDrama1.qa
- `entertainment#12` (bein.com — beINGOURMET): channel already covered by v1 beINGourmet.qa
- `entertainment#23` (bein.com — beINJUNIOR): channel already covered by v1 BeJunior.qa
- `entertainment#9` (bein.com — beINSERIES1): channel already covered by v1 beINSeries1.qa

### US-only channel (no MENA equivalent in pack) (1)

- `beINSportsUSA.us` (beinsports.com — beIN SPORTS): US channel; the pack has only the MENA main beIN SPORTS channel

### no id for this channel in the pack (35)

- `1101` (osn.com — KTV Channel 1 HD): no candidate in Online4Tech pack
- `206` (osn.com — Blippi and Friends): no candidate in Online4Tech pack
- `221` (osn.com — OSNtv iQIYI): no candidate in Online4Tech pack
- `226` (osn.com — OSNtv Pop Up 2): no candidate in Online4Tech pack
- `314` (osn.com — OSNtv Documentary): no candidate in Online4Tech pack
- `520D107A-71D4-4CB7-B141-1C6B089A7FFC` (beinsports.com — BEINS8C): no candidate in Online4Tech pack
- `5824C394-7211-4004-AC46-35BD58B9D1EE` (beinsports.com — BEINSSC): no candidate in Online4Tech pack
- `5ED9E1C4-BEF4-4AC2-8F90-28B3DCA26375` (beinsports.com — BEINC): no candidate in Online4Tech pack
- `6609` (osn.com — Esport 24): no candidate in Online4Tech pack
- `6611` (osn.com — Padel TV): no candidate in Online4Tech pack
- `846C79D6-18F8-4A4D-ACFA-2C18DCCB6398` (beinsports.com — beIN SPORTS EN 2): no candidate in Online4Tech pack
- `8C1EC4FC-35E6-4866-A75D-37FCFAE18839` (beinsports.com — beIN SPORTS EN 1): no candidate in Online4Tech pack
- `93000494-0DF8-4107-AF0E-1C99D3DBB2EC` (beinsports.com — beIN SPORTS FR 1): no candidate in Online4Tech pack
- `9957` (osn.com — STV1 HD): no candidate in Online4Tech pack
- `9B969275-E59C-4DD1-8FCA-8B01EAE04909` (beinsports.com — beIN SPORTS FR 2): no candidate in Online4Tech pack
- `AlManar.lb` (elcinema.com — Al-Manar; المنار): no candidate in Online4Tech pack
- `Baraem.qa` (bein.com — BaraemTV): no candidate in Online4Tech pack
- `C938A2D0-375A-4876-B05D-08EE29D33B07` (beinsports.com — beIN SPORTS XTRA): no candidate in Online4Tech pack
- `MCMTop.fr` (osn.com — MCM TOP): no candidate in Online4Tech pack
- `Masah.sa` (elcinema.com — Masah; ماسة): no candidate in Online4Tech pack
- `MotorvisionPlus.de` (osn.com — MOTORVISION): no candidate in Online4Tech pack
- `NationalGeographicMiddleEast.uk` (elcinema.com — National Geogra...; ناشيونال جيوجرافيك): no candidate in Online4Tech pack
- `RFMTV.fr` (osn.com — RFM TV): no candidate in Online4Tech pack
- `beINSPORTSXTRA.us` (beinsports.com — beIN SPORTS XTRA): no candidate in Online4Tech pack
- `beINSPORTSXTRAenEspanol.us` (beinsports.com — beIN SPORTS XTRA ñ): no candidate in Online4Tech pack
- `beINSportsMax10.qa` (beinsports.com — beIN SPORTS MAX 10): no candidate in Online4Tech pack
- `beINSportsMax7.qa` (beinsports.com — beIN SPORTS MAX 7): no candidate in Online4Tech pack
- `beINSportsMax8.qa` (beinsports.com — beIN SPORTS MAX 8): no candidate in Online4Tech pack
- `beINSportsMax9.qa` (beinsports.com — beIN SPORTS MAX 9): no candidate in Online4Tech pack
- `beINSportsenEspanol.qa` (beinsports.com — beIN SPORTS Español): no candidate in Online4Tech pack
- `entertainment#24` (bein.com — JeemTV): no candidate in Online4Tech pack
- `entertainment#30` (bein.com — 30): no candidate in Online4Tech pack
- `entertainment#31` (bein.com — 31): no candidate in Online4Tech pack
- `entertainment#8` (bein.com — 8): no candidate in Online4Tech pack
- `sports#16` (bein.com — 16): no candidate in Online4Tech pack

### look-alike twin in pack — deliberately not guessed (7)

- `ATV.kw` (elcinema.com — atv; إيه تي في): no Adala TV id in the pack; 'ATV Kurd' is a Kurdish channel
- `AlarabiyaPortrait.ae` (osn.com — Al Arabiya): no Portrait feed id in the pack; 'Alarabiya.ae' is the main Al Arabiya feed (Portrait likely simulcasts it — needs confirmation)
- `CNNArabic.ae` (bein.com — 26; 27): no CNN Arabic id in the pack; 'CNN' is the English channel
- `FoxArabia.ae` (bein.com — 13): no Fox Arabia id in the pack; 'FOX-HD' is the English Fox channel (likely twin 'Fox Be Elaraby TV' needs confirmation)
- `FoxLifeMiddleEast.ae` (bein.com — 18): no Fox Life id in the pack; 'FOX-HD' is the main Fox channel
- `MBCMood.sa` (osn.com — MBC Mood): no MBC Mood id in the pack; 'MBC' is the main MBC 1 channel
- `SaudiThaqafiyaTV.sa` (osn.com — Al Thaqafeya): no Thaqafiya/Culture id in the pack; 'Saudi TV' is the main Saudi channel

## What this means for the daily generator

- bein.com: 58/76 channels will now remap (was 46/76 in v1). The 18 unmapped are mostly US/regional feeds (EN/FR/ES, Max 7–10, Español, Baraem, bare-number slugs with no signal) — no MENA beIN channel is left without a feed except the twins listed above.
- osn.com: 66/80 (was 52/80). The 14 unmapped are channels with no pack id (KTV 1, Blippi, iQIYI, Pop Up 2, Documentary, Esport 24, Padel TV, STV1, MCM Top, Motorvision, RFM) plus the deliberate twin skips (MBC Mood, Al Arabiya Portrait, Al Thaqafeya).
- elcinema.com: 101/105 (was 99/105). Unmapped: Al-Manar, Masah, National Geographic Middle East, ATV (twin skip).
- beinsports.com: 28/63 (was 13/63). The 35 unmapped are mostly non-MENA UUIDs (Malaysia/New Zealand/Australia/France feeds of Sports 1/2/3, EN/FR feeds) and duplicate MENA feeds dropped by the guard — the MENA channel itself is covered in every case except Sports 2/3, which have NO MENA beinsports.com feed (their MENA schedule comes from the bein.com base ids `beINSports2/3.qa` → `_PREMIUM`, already in v1).
- Expected effect on the next generator run: bein.com.xml should fill from 2 channels to ~58, osn.com.xml from 0 to ~66 (limited by the OSN site itself returning programmes for only 4 channels), beinsports.com.xml from 0 to ~28, elcinema.com.xml from 0 to ~101 (subject to its 429 rate-limit).

## Files

- `id-mapping.json` — 213 entries (this report's subject).
- Builder: `/tmp/build-mapping-v2.py` (not in this dir — the task scoped this dir to the mapping + the report). State: `/tmp/mapping-state-v2.json`.
- v1 copy used as the restore point: `/tmp/id-mapping-v1.json` (170 entries, fetched from GitHub raw).
- Pack reference: `~/workspace/epg-research/online4tech-epg-pack/` (2,020 unique channel ids across the 3 channels files).
- Grabber lists: `~/workspace/epg-research/epg-tool-test/sites/` (cloned iptv-org/epg repo).