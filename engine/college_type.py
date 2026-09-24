"""Classifies an institute as Government or Private/Deemed for the
Predictor's "Government seats only" filter.

Why this exists: the real MCC allotment data mixes three very different
kinds of seats under one "institute" list --

  1. Government medical colleges (state, central, municipal, defence,
     railways, ESIC) -- what most NEET-PG aspirants mean by "a government
     seat".
  2. Private and deemed-university medical colleges (much higher fees,
     run by a trust/society) -- MD/MS and Diploma seats.
  3. NBEMS DNB/Diploma seats at individual ACCREDITED HOSPITALS -- mostly
     private or trust hospitals (Apollo, Narayana, hundreds of small
     nursing-home-scale hospitals), though a handful are genuinely
     government (district hospitals, ESIC, defence, railway hospitals).

Across the 3 real datasets currently loaded there are ~1,570 distinct
institute names, of which ~1,000 are DNB-accredited hospitals and ~630 are
Diploma-accredited hospitals -- both categories are overwhelmingly private,
and blending them into the same "seats" figure as real government medical
college seats is exactly what was making the Predictor's numbers look
inflated and inconsistent with what a candidate could actually expect at a
government college's closing rank.

How this file classifies:
  - GOVERNMENT_KEYWORDS: a name containing one of these is confidently
    government, whichever specific college it is (the ownership signal is
    in the name itself: "Government Medical College", "ESIC ...", "Command
    Hospital", "Autonomous State Medical College", etc.)
  - KNOWN_GOVERNMENT: well-known government medical colleges/institutes
    whose name does NOT carry an obvious government keyword (e.g. "Grant
    Medical College", "Maulana Azad Medical College", "Tata Memorial
    Centre" -- the last is a Government of India / Dept. of Atomic Energy
    institution despite the "Tata" name).
  - KNOWN_PRIVATE: well-known private / trust / deemed-university medical
    colleges whose name does not obviously say so (e.g. "Kasturba Medical
    College Manipal", "JSS Medical College", "Amrita School of Medicine").
  - Everything else is "unverified" -- NOT assumed to be government. Some
    names are used by more than one institution of different ownership
    (e.g. a bare "Jawaharlal Nehru Medical College" or "Institute of
    Medical Sciences" is used by both a government and a private college
    elsewhere in India), and the vast majority of unmatched names are the
    small private/trust hospitals that only offer DNB/Diploma seats. Rather
    than guess, unverified institutes are excluded from the "Government
    seats" view and shown separately in "All seats" as "ownership not yet
    verified" -- consistent with the project's rule to never publish an
    unvalidated classification as if it were confirmed.

This is a best-effort, hand-reviewed classification, not an official MCC/
NMC list -- if you (or a candidate) spot a college classified wrong, that
is exactly the kind of thing this file should be corrected for. A more
authoritative fix would cross-check every institute against NMC's own
published college directory (which records ownership type); that is future
work, tracked as a known limitation rather than silently assumed away.
"""

from __future__ import annotations

import re

GOVERNMENT_KEYWORDS = [
    "government", "govt", "govermen", "gvernment",  # incl. common typos seen in real PDFs
    "rajkiya",  # Hindi for "state-run" / government
    "esic", "esi-", "employees' state insurance", "employees state insurance",
    "armed forces medical college", "command hospital", "army hospital",
    "institute of naval medicine", "institute of aerospace medicine",
    "air force hospital",
    "railway",
    "autonomous state medical college",
    "district hospital", "area hospital",
    "municipal corporation",
    "state medical college",
    "state institute of medical sciences",
]

# Well-known government (state/central/municipal/defence/PSU) institutes
# whose name has no obvious "government" marker.
KNOWN_GOVERNMENT = {
    "grant medical college",
    "maulana azad medical college",
    "madras medical college",
    "bangalore medical college and research institute",
    "osmania medical collge",
    "osmania medical college",
    "stanley medical college",
    "king georges medical university",
    "king george's medical university",
    "seth gordhandas sunderdas medical college",
    "b. j. medical college",
    "sawai man singh medical college",
    "university college of medical sciences",
    "vardhman mahavir medical college",
    "lady hardinge medical college",
    "topiwala national medical college",
    "lokmanya tilak medical college mumbai",
    "pgimer",
    "regional institute of medical sciences",
    "rajiv gandhi institute of medical sciences",
    "rajiv gandhi medical college kalwa thane",
    "sanjay gandhi postgarduate institute of medical sciences",
    "sanjay gandhi institute of trauma and orthopaedics",
    "sardar patel medical college",
    "sarojini naidu medical college",
    "sher-i-kashmir institute of medical sciences",
    "institute of naval medicine",
    "institute of aerospace medicine",
    "indian railway post graduate institute of medical sciences and research and associated northern railway central hospital",
    "the national institute of health and family welfare",
    "vallabhbhai patel chest institute",
    "chittaranjan national cancer institute",
    "chittaranjan seva sadan hospital",
    "tata memorial centre",  # Govt of India, Dept. of Atomic Energy
    "homi bhabha cancer hospital",
    "homi bhabha cancer hospital and research centre",
    "kidwai memorial institute of oncolgy",
    "malabar cancer centre post graduate institute of oncology sciences and research",
    "regional cancer centre",
    "north eastern indira gandhi regional institute of health & medical sciences",
    "central institute of psychiatry",
    "g b pant institute of post graduate medical education and research",
    "pandit bhagwat dayal sharma post graduate institute of medical sciences",
    "post graduate institute of medical sciences (pgims)",
    "gandhi medical college",
    "andhra medical college",
    "assam medical college",
    "gauhati medical college",
    "guntur medical college",
    "kurnool medical college",
    "burdwan medical college",
    "nil ratan sircar medical college",
    "r g kar medical college",
    "calcutta national medical college",
    "midnapore medical college and hospital",
    "north bengal medical college",
    "patna medical college",
    "nalanda medical college",
    "darbhanga medical college",
    "chengalpattu medical college",
    "coimbatore medical college",
    "madurai medical college",
    "thanjavur medical college",
    "tirunelveli medical college",
    "government kilpauk medical college",
    "jawaharlal institute of medical sciences",  # JIPMER
    "kalpana chawla govt medical college",
    "maharani laxmi bai medical college jhansi",
    "moti lal nehru medical college",
    "sri venkateswara institute of medical sciences (svims)",
    "institute of child health",
    "indira gandhi institute of child health",
    "post graduate institute of child health",
    "dr. b. c. roy post graduate institute of paediatric sciences",
    # Karnataka's district-headquarters government medical colleges
    # (all part of the same state-run expansion, ~2018-2020 onward)
    "belagavi institute of medical sciences",
    "bidar institute of medical sciences",
    "chikkamagaluru institute of medical science",
    "chamarajanagar institute of medical sciences",
    "gadag institute of medical sciences gadag",
    "hassan institute of medical sciences",
    "haveri institute of medical sciences",
    "karwar institute of medical sciences",
    "kodagu institute of medical sciences",
    "koppal institute of medical sciences koppal",
    "mandya institute of medical sciences",
    "raichur institute of medical sciences",
    "shimoga institute of medical sciences",
    "vijanagara institute of medical sciences ballari",
    "gulbarga institute of medical sciences",
    "mysore medical college and research institute",
    # West Bengal government medical colleges
    "bankura sammilani medical college",
    "college of medicine & sagore dutta hospital",
    "college of medicine and jnm hospital",
    "murshidabad medical college and hospital",
    "malda medical college",
    "nil ratan sircar medical college",
    "r g kar medical college",
    "calcutta national medical college",
    "midnapore medical college and hospital",
    "north bengal medical college",
    "ipgme&r and sskm hospital kolkata",
    "burdwan medical college",
    # Odisha government medical colleges / institutes
    "srirama chandra bhanja medical college",
    "maharaja krushna chandra gajapati medical college",
    "bhima bhoi medical college & hospital",
    "fakir mohan medical college and hospital",
    "pt. raghunath murmu medical college & hospital",
    "acharya harihar post graduate institute of cancer",
    "vss institute of medical sciences and research",
    "post graduate institute of medical education & research and capital hospital ( pgimer & ch)",
    # Uttar Pradesh government medical colleges
    "ganesh shankar vidyarthi memorial medical college",
    "baba raghav das medical college",
    "gajra raja medical college gwalior",
    "shyam shah medical college",
    "netaji subhash chandra bose medical college",
    "gwalior mansik arogyashala",
    "mahamaya rajkiya allopathic medical college",
    "gmc bharat ratna late shri atal bihari vajpayee memorial medical college",
    "shaikh-ul-hind maulana mahmood hasan medical college",
    "dr ram manohar lohia institute of medical sciences",
    "dr. b r ambedkar state institute of medical sciences",
    "uttar pradesh university of medical sciences",
    "hindu rao hospital delhi",
    "kasturba hospital",
    "chacha nehru bal chikitsalaya",
    "institute of human behaviour and allied sciences",
    "pt. jawahar lal nehru memorial medical college",
    # Bihar / Jharkhand government medical colleges
    "indira gandhi institute of medical sciences",
    "shrikrishna medical college & hospital",
    "rajendra institute of medical sciences",
    "shaheed nirmal mahto medical college & hospital",
    "anugrah narayan magadh medical college",
    "anugrah narayan magdh medical college gaya",
    # Rajasthan / Gujarat government medical colleges
    "dr. sampurnanand medical college (snmc)",
    "jhalawar medical college",
    "pandit dindayal upadhyay medical college",
    "vardhman institute of medical sciences",
    "smt. g. r. doshi and smt. k. m. mehta institute of kidney diseases & research centre dr. h. l. trivedi institute of transplantation sciences (ikdrc-its)",
    "ruhs college of medical sciences",
    # Andhra Pradesh / Telangana government medical colleges
    "s.v. medical college",
    "kakatiya medical college",
    "rangaraya medical college",
    "siddhartha medical college",
    "rajiv gandhi institute of medical sciences srikakulam",
    "nizams institute of medical sciences",
    "institute of mental health and hospital",
    # Punjab / Chhattisgarh government medical colleges
    "guru gobind singh medical college",
    # Assam / Northeast government medical colleges
    "silchar medical college",
    "tezpur medical college",
    "lakhimpur medical college",
    "jorhat medical college & hospital",
    "diphu medical college & hospital",
    "fakhruddin ali ahmed medical college",
    "zoram medical college & hospital",
    "tomo riba institute of health and medical sciences",
    "dr.b.borooah cancer institute",
    "lokopriya gopinath bordoloi regional institute of mental health",
    "andaman & nicobar islands institute of medical sciences",
    "namo medical education and research institute",
    "indira gandhi medical college shimla",
    "indira gandhi medical college and research institute",
    # Central / autonomous government institutes
    "all india institute of hygiene and public health",
    "all india institute of physical medicine and rehabilitation",
    "bhopal memorial hospital and research centre",
    "radiation medicine centre (rmc)",
    "sds tuberculosis research centre and rajiv gandhi institute of chest diseases",
    "dharwad institute of mental health and neurosciences (dimhans)",
    "goa medical college",
    "maharashtra post graduate institute of medical education and research",
    "rims medical college",
    "regional institute of ophthalmology",
    "mahatma gandhi memorial medical college",
    "ravindra nath tagore medical college",
    "rajkiya medical college",
    "chhattisgarh institute of medical sciences",
    "calcutta school of tropical medicine",
    "lala lajpat rai memorial medical college",
    "hinduhridayasamrat balasaheb thackeray medical college and dr. r. n. cooper municipal general hospital",
}

# Well-known private / trust / deemed-university medical colleges whose
# name has no obvious "private"/"deemed" marker.
KNOWN_PRIVATE = {
    "amrita school of medicine",
    "bharati vidyapeeth (deemed to be university) medical college and hospital",
    "bharati vidyapeeth deemed to be university medical college",
    "d. y. patil medical college",
    "dr d y patil medical college",
    "dr. d. y. patil medical college",
    "datta meghe medical college wanadongri",
    "jss medical college",
    "k s hegde medical academy",
    "kasturba medical college mangalore",
    "kasturba medical college manipal",
    "kalinga institute of medical sciences",
    "krishna institute of medical sciences",
    "m.m. institute of medical sciences and research",
    "meenakshi medical college hospital and research institute",
    "pravara rural medical college",
    "santosh medical college and hospital",
    "saveetha medical college nd hospital",
    "sbks medical college and research centre",
    "sree balaji medical college and hospital",
    "sri devaraj urs medical college",
    "sri lakshmi narayana institute of medical sciences",
    "sri ramachandra medical college and research institute",
    "sri siddhartha medical college",
    "sri siddhartha institute of medical sciences & research centre (ssimrc)",
    "srm medical college hospital and research centre",
    "symbiosis medical college for women",
    "vinayaka missions medical college and hospital",
    "vinayaka missions kirupananda variyar medical college and hospital",
    "vels medical college & hospital",
    "yenepoya medical college",
    "gitam institute of medical sciences & research",
    "malla reddy institute of medical sciences",
    "malla reddy medical college for women",
    "a.c.s. medical college and hospital",
    "aarupadai veedu medical college and hospital",
    "rajarajeswari medical college and hospital",
    "sri lalithambigai medicl college and hospital",
    "hamdard institute of medical sciences and research",
    "shri sathya sai medical college and research institute",
    "mahatma gandhi medical college and research institute",
    "institute of medical sciences and sum hospital",
    "chettinad hospital and research institute",
    "santosh medical college",
    "karnataka medical college and research institute",
    "bhaarath medical college and hospital",
    "shri atal bihari vajpayee medical college & research institute",
    "sri sri lalithambigai medical college and hospital",
    "aarti scans pvt ltd",
    "mahatma gandhi institute of medical sciences",  # Sevagram (Kasturba Health Society) -- distinct from govt "...Memorial Medical College" Indore
    "st. philomena`s hospital",
    "lalitha super specialty hospital",
    "starcare hospital kozhikode private limited",
    "yashoda health care services private limited",
    "alchemist hospital",
    "shri. b. m. patil medical college hospital and research centre",  # BLDE (Deemed University), Vijayapura
}

# Genuinely ambiguous: the same name is used by both a government and a
# private/deemed institution elsewhere in India, and the dataset does not
# carry enough detail (city/state) to tell which one a given row means.
# Deliberately left unclassified rather than guessed either way.
AMBIGUOUS_NAMES = {
    "jawaharlal nehru medical college",  # govt (Bhagalpur) vs private-deemed (KLE, Belagavi)
    "jawahar lal nehru medical college",
    "institute of medical sciences",  # bare -- could be BHU-IMS (govt) or a generic label
    "mgm medical college",  # govt (Indore) vs private (Navi Mumbai, Jamshedpur)
    "medical college",  # too generic to identify
}


def _norm(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip()).lower()


def classify(institute: str) -> str:
    """Returns 'government', 'private', or 'unverified' for an institute
    name as it appears in the extracted MCC data (post clean_institute())."""
    n = _norm(institute)
    if n in AMBIGUOUS_NAMES:
        return "unverified"
    for kw in GOVERNMENT_KEYWORDS:
        if kw in n:
            return "government"
    if n in KNOWN_GOVERNMENT:
        return "government"
    if n in KNOWN_PRIVATE:
        return "private"
    return "unverified"
