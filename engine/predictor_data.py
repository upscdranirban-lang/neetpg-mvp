"""Third-party-sourced NEET-PG 2025 rank data used ONLY by the demo
rank/branch predictor.

IMPORTANT -- this file is intentionally kept separate from the rest of
the engine (engine/db.py etc.), which stores only officially-sourced MCC
documents. Everything in here was copied from third-party exam-prep
websites (not MCC), because MCC does not publish a "closing rank" table
directly -- see the design doc's "cutoffs are derived, never official"
note. These specific numbers are ALSO not derived from an MCC document we
hold; they are someone else's already-derived numbers, one layer further
from the source than our own /neet-pg/cutoff pages will eventually be
once Phase 3 parses real MCC allotment result PDFs.

That means, compared to the rest of the platform:
  - no official source URL/date for these individual numbers
  - not versioned across our own audit trail
  - not cross-checked against MCC's own result PDF
  - round coverage is inconsistent (mostly Round 1; Round 2 open-category
    only; no Round 3 or Stray data found on any of the 5 sources checked)

So the site must show this behind an unmistakable "ESTIMATE, not MCC
data" wall, never blended into the Archive/Updates pages that carry real
provenance. See site/index.html's Predictor tab.

Sources checked (7 total across two rounds of searching -- the request
was "first five authentic sources," but only 3 of the sources found
across both searches actually had extractable, round-labeled numbers;
the rest were "expected/forecast" marketing articles with no real
reported data, and were excluded rather than counted just to hit five):

  1. Careers360 (medicine.careers360.com) -- college-wise opening/closing
     ranks, OPEN/UR category only, for 5 specialties, "NEET PG Cut Off
     2025 Out: Opening and Closing Ranks for Government Colleges"
  2. FindMyCollege (articles.findmycollege.com) -- specialty-wise
     closing ranks by category (Open/OBC/SC/ST), Round 1 only in full,
     "NEET PG Counselling 2025 Cut Off"
  3. Shiva Learning (shivalearning.com) -- specialty-wise closing ranks
     by category (Open/OBC/EWS/SC/ST), Round 1 AND Round 2, "NEET PG
     2025 All India Quota (50%) Cut-Off". This is the most complete
     specialty-level table found and supersedes source #2's numbers
     below (they agree wherever both report a figure).

  Checked and excluded (forecast/marketing, not reported results):
  PW Live (pw.live), Sartha (sartha.in), NEET Counselling 2026
  (neetcounseling2026.com), Diginerve (diginerve.com).

No source found (across ~4 separate searches) publishes COLLEGE-level
closing ranks broken down by category (OBC/EWS/SC/ST) -- every
college-wise table found is Open/UR only. See CATEGORY_ADJUSTMENT_NOTE
below for how the site fills that gap, and how that fill is labeled.

Retrieved: 2026-09-21.
"""

from __future__ import annotations

SOURCES = [
    {
        "name": "Careers360",
        "url": "https://medicine.careers360.com/articles/neet-pg-cut-off",
        "used_for": "college-wise opening/closing ranks, Open category (5 specialties)",
    },
    {
        "name": "Shiva Learning",
        "url": "https://shivalearning.com/neet-pg-2025-all-india-quota-50-cut-off/",
        "used_for": "specialty-wise closing ranks, all categories (Open/OBC/EWS/SC/ST), Round 1 & 2",
    },
    {
        "name": "FindMyCollege",
        "url": "https://articles.findmycollege.com/neet-pg-counselling-2025-cut-off/",
        "used_for": "specialty-wise closing ranks by category, Round 1 (cross-check for Shiva Learning)",
    },
]

NOT_USED = [
    "PW Live (pw.live) -- 'expected' forecast, not a reported result",
    "Sartha (sartha.in) -- 'expected' forecast, not a reported result",
    "NEET Counselling 2026 (neetcounseling2026.com) -- 'expected' forecast, not a reported result",
    "Diginerve (diginerve.com) -- 'expected' forecast, not a reported result",
]

CATEGORY_ADJUSTMENT_NOTE = (
    "No source publishes college-level closing ranks by category (only "
    "Open/UR college-wise data exists). For OBC/EWS/SC/ST in the College "
    "Predictor, this demo CALCULATES an estimate: it scales each "
    "college's reported Open closing rank by the category-vs-Open gap "
    "seen at the specialty level (Round 1, from Shiva Learning). This is "
    "a derived estimate, not a reported number, and is labeled as such "
    "everywhere it's shown -- it can be significantly wrong for any "
    "individual college, since the real category gap varies by college, "
    "not just by specialty."
)

# Closing rank by specialty x category x round, from Shiva Learning --
# the most complete of the three specialty-level sources (has EWS and
# both rounds for every category). None = that source showed no seats
# filled/reported in that category+round for that specialty.
# columns: (specialty, Open_R1, Open_R2, OBC_R1, OBC_R2, EWS_R1, EWS_R2, SC_R1, SC_R2, ST_R1, ST_R2)
SPECIALTY_ALL_CATEGORIES = [
    ("Nuclear Medicine", 658, 845, 1549, 2844, None, None, None, None, None, None),
    ("Dermatology", 2725, 6251, 5653, 7099, 6713, 9641, 12811, 17079, 25808, 28002),
    ("Radio-Diagnosis", 2920, 4137, 3936, 6067, 4586, 5998, 9941, 12903, 17238, 21007),
    ("General Medicine", 3822, 6070, 6301, 7991, 7655, 8716, 17908, 21968, 33062, 36729),
    ("Paediatrics", 7071, 9591, 10534, 12029, 11024, 14851, 22979, 31803, 47281, 51217),
    ("Obstetrics & Gynaecology", 9714, 11555, 14008, 15380, 16826, 18281, 31068, 37930, 50317, 58481),
    ("Respiratory Medicine", 9780, 11803, 13828, 16981, 16204, 17912, 33686, 34591, 54653, 59581),
    ("Sports Medicine", 9850, 15768, 11747, None, 19596, None, None, None, None, None),
    ("Geriatrics", 10451, 12219, 12420, None, 15407, None, 35107, None, 55338, 71481),
    ("General Surgery", 11507, 15331, 15525, 18300, 17957, 22784, 33129, 39530, 55932, 68175),
    ("Orthopaedics", 12429, 17062, 14894, 18870, 19488, 21623, 34943, 39123, 53647, 71600),
    ("Palliative Medicine", 13211, 16700, None, None, 37000, None, 40392, None, 47230, None),
    ("Emergency Medicine", 13772, 17208, 15397, 18941, 23147, 29384, 29247, 39726, 61712, 79656),
    ("Psychiatry", 16458, 19214, 22415, 17581, 31680, 37502, 37273, 43493, 72084, 87834),
    ("Ophthalmology", 16969, 19730, 20787, 26853, 24222, 32401, 38106, 44789, 67111, 81002),
    ("Radiotherapy", 17190, 22254, 22719, 28034, 25863, 28039, 39994, 41933, None, None),
    ("ENT", 17851, 21089, 22080, 29167, 26569, 30734, 39073, 45819, 69115, 71385),
    ("Anaesthesiology", 19028, 24796, 25331, 31630, 27628, 36435, 43389, 49689, 60974, 76232),
    ("PMR", 23132, 25038, 33452, None, 34354, None, 42169, None, 68021, 83766),
    ("IHBT", 29147, 40064, 32794, 50551, 37846, 50247, 53864, None, 92108, 85523),
    ("Hospital Administration", 29826, 36253, 34882, None, 37125, None, 66596, None, None, None),
    ("Pathology", 36444, 47475, 43765, 55390, 62085, 69470, 64648, 83070, 75436, 67360),
    ("PSM", 54470, 69799, 63587, 84655, 102408, 108389, 101936, 114739, 90583, 111103),
    ("Microbiology", 64970, 84241, 81898, 103039, 111558, 111558, 109539, 131799, 99228, 122647),
    ("Pharmacology", 68792, 88005, 88974, 115944, 112327, 111586, 105320, 129557, None, None),
    ("Forensic Medicine", 72787, 98148, 85418, 112342, 115201, 113950, 100985, 119828, None, None),
    ("Biochemistry", 91932, 115178, 109052, 134046, 115473, 112255, 135908, 129894, None, None),
    ("Physiology", 105948, 114208, 127756, 138605, 112245, 115305, 134723, 134971, None, None),
    ("Anatomy", 110157, 114364, 135658, 136606, 115305, 112763, 136069, 136069, None, None),
]

# College-wise opening/closing rank, Open/UR category, round/date not
# specified by the source beyond "NEET PG 2025" -- treat as an
# end-of-counselling (post Round 2, pre Round 3) snapshot, not tied to a
# specific round. Only 5 specialties had college-level tables.
COLLEGE_RANKS = {
    "General Medicine": [
        ("Atal Bihari Vajpayee Institute of Medical Sciences and Dr Ram Manohar Lohia Hospital, New Delhi", 1, 15),
        ("Nizams Institute of Medical Sciences, Hyderabad", 16, 16),
        ("Maulana Azad Medical College, New Delhi", 34, 62),
        ("Vardhman Mahavir Medical College and Safdarjung Hospital, New Delhi", 30, 74),
        ("Lady Hardinge Medical College for Women, New Delhi", 75, 83),
        ("Government Medical College and Hospital, Chandigarh", 107, 107),
        ("Government Medical College, Thrissur", 114, 114),
        ("Lokmanya Tilak Municipal Medical College, Mumbai", 47, 119),
        ("Seth GS Medical College (KEM), Mumbai", 44, 125),
        ("Government Medical College, Kozhikode", 2, 129),
        ("University College of Medical Sciences, Delhi", 164, 164),
        ("B J Medical College, Ahmedabad", 19, 170),
        ("Institute of Medical Sciences, BHU, Varanasi", 124, 176),
        ("Government Medical College, Kottayam", 71, 200),
        ("IPGMER, Kolkata", 198, 201),
        ("Bangalore Medical College and Research Institute, Bangalore", 8, 228),
        ("Madras Medical College, Chennai", 9, 291),
        ("Topiwala National Medical College (Nair), Mumbai", 181, 294),
        ("Government Medical College, Thiruvananthapuram", 183, 308),
        ("Karnataka Institute of Medical Sciences, Hubli", 267, 327),
    ],
    "Radio-Diagnosis": [
        ("Vardhman Mahavir Medical College and Safdarjung Hospital, New Delhi", 4, 25),
        ("Government Medical College and Hospital, Chandigarh", 39, 39),
        ("Seth GS Medical College (KEM), Mumbai", 24, 58),
        ("Maulana Azad Medical College, New Delhi", 42, 60),
        ("Atal Bihari Vajpayee Institute of Medical Sciences and Dr Ram Manohar Lohia Hospital, New Delhi", 70, 73),
        ("Government Medical College, Kozhikode", 35, 79),
        ("Bangalore Medical College and Research Institute, Bangalore", 50, 80),
        ("Nizams Institute of Medical Sciences, Hyderabad", 90, 98),
        ("Sanjay Gandhi PGI, Lucknow", 100, 104),
        ("Lady Hardinge Medical College for Women, New Delhi", 108, 108),
        ("Government Medical College, Thiruvananthapuram", 101, 118),
        ("Grant Medical College and Sir JJ Hospital, Mumbai", 122, 145),
        ("Madras Medical College, Chennai", 28, 156),
        ("Institute of Medical Sciences, BHU, Varanasi", 120, 179),
        ("Government Medical College, Kottayam", 184, 184),
        ("University College of Medical Sciences, Delhi", 116, 187),
        ("Patna Medical College, Patna", 191, 191),
        ("B J Medical College, Ahmedabad", 17, 203),
        ("Lokmanya Tilak Municipal Medical College, Mumbai", 96, 209),
        ("Pt B D Sharma PGIMS, Rohtak", 266, 266),
        ("King George's Medical University, Lucknow", 236, 274),
        ("Sawai Man Singh Medical College, Jaipur", 18, 289),
        ("NEIGRIHMS, Shillong", 297, 297),
        ("IPGMER, Kolkata", 155, 309),
        ("Government Medical College, Kota", 317, 317),
        ("Jawaharlal Nehru Medical College, AMU, Aligarh", 113, 326),
        ("Government Medical College, Nagpur", 264, 357),
    ],
    "Dermatology": [
        ("Government Medical College, Kozhikode", 20, 20),
        ("Lokmanya Tilak Municipal Medical College, Mumbai", 102, 102),
        ("Vardhman Mahavir Medical College and Safdarjung Hospital, New Delhi", 91, 142),
        ("Grant Medical College and Sir JJ Hospital, Mumbai", 255, 255),
        ("Bangalore Medical College and Research Institute, Bangalore", 275, 275),
        ("Government Medical College, Thiruvananthapuram", 186, 282),
        ("Government Medical College, Kottayam", 302, 302),
        ("Lady Hardinge Medical College for Women, New Delhi", 359, 359),
        ("Atal Bihari Vajpayee Institute of Medical Sciences and Dr Ram Manohar Lohia Hospital, New Delhi", 29, 364),
        ("BJ Government Medical College, Pune", 298, 387),
        ("Institute of Medical Sciences, BHU, Varanasi", 371, 392),
        ("Government Medical College and Hospital, Chandigarh", 394, 394),
        ("Sawai Man Singh Medical College, Jaipur", 244, 398),
        ("Government Medical College, Thrissur", 422, 422),
        ("T D Medical College, Alappuzha", 482, 482),
        ("MKCG Medical College, Berhampur", 506, 506),
        ("PCMC PG Institute (YCM Hospital), Pimpri", 525, 525),
        ("Pt B D Sharma PGIMS, Rohtak", 549, 549),
        ("Jawaharlal Nehru Medical College, AMU, Aligarh", 557, 557),
        ("Karnataka Institute of Medical Sciences, Hubli", 610, 610),
        ("B J Medical College, Ahmedabad", 605, 634),
        ("Shivamogga Institute of Medical Sciences, Shimoga", 642, 642),
        ("Rabindra Nath Tagore Medical College, Udaipur", 233, 671),
    ],
    "General Surgery": [
        ("Maulana Azad Medical College, New Delhi", 110, 123),
        ("Vardhman Mahavir Medical College and Safdarjung Hospital, New Delhi", 172, 322),
        ("Atal Bihari Vajpayee Institute of Medical Sciences and Dr Ram Manohar Lohia Hospital, New Delhi", 52, 419),
        ("University College of Medical Sciences, Delhi", 456, 456),
        ("Grant Medical College and Sir JJ Hospital, Mumbai", 95, 564),
        ("Lady Hardinge Medical College for Women, New Delhi", 480, 732),
        ("Government Medical College, Kozhikode", 640, 1035),
        ("Institute of Medical Sciences, BHU, Varanasi", 964, 1221),
        ("Lokmanya Tilak Municipal Medical College, Mumbai", 451, 1257),
        ("BJ Government Medical College, Pune", 1171, 1295),
        ("Seth GS Medical College (KEM), Mumbai", 382, 1328),
        ("Topiwala National Medical College (Nair), Mumbai", 1391, 1777),
        ("B J Medical College, Ahmedabad", 1016, 1830),
        ("ESIC Medical College, Hyderabad", 1903, 1988),
        ("Stanley Medical College, Chennai", 1141, 2082),
        ("Government Medical College, Kottayam", 807, 2138),
        ("Government Medical College and Hospital, Chandigarh", 1310, 2191),
        ("HBT Medical College and Dr RN Cooper Hospital, Mumbai", 2210, 2210),
        ("Osmania Medical College, Hyderabad", 22, 2395),
        ("Gandhi Medical College and Hospital, Secunderabad", 173, 2436),
        ("Sawai Man Singh Medical College, Jaipur", 813, 2450),
        ("Government Medical College, Surat", 503, 2476),
        ("Government Medical College, Thiruvananthapuram", 313, 2540),
    ],
    "Obstetrics & Gynaecology": [
        ("Lady Hardinge Medical College for Women, New Delhi", 56, 324),
        ("Vardhman Mahavir Medical College and Safdarjung Hospital, New Delhi", 14, 541),
        ("Maulana Azad Medical College, New Delhi", 490, 806),
        ("Lokmanya Tilak Municipal Medical College, Mumbai", 469, 949),
        ("Atal Bihari Vajpayee Institute of Medical Sciences and Dr Ram Manohar Lohia Hospital, New Delhi", 438, 1177),
        ("University College of Medical Sciences, Delhi", 1030, 1320),
        ("B J Medical College, Ahmedabad", 329, 1331),
        ("ESI PGIMSR, New Delhi", 1337, 1337),
        ("Madras Medical College, Chennai", 12, 1434),
        ("Sher-I-Kashmir Institute of Medical Sciences, Srinagar", 1482, 1482),
        ("Gandhi Medical College and Hospital, Secunderabad", 474, 1584),
        ("Government Medical College and Hospital, Chandigarh", 1588, 1588),
        ("Bangalore Medical College and Research Institute, Bangalore", 547, 1601),
        ("Institute of Medical Sciences, BHU, Varanasi", 1939, 1939),
    ],
}
