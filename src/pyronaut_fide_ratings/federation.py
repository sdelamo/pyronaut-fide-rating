# FIDE federation code -> (name, ISO 3166-1 alpha-2 code, or the ISO 3166-2 code for a UK nation).
# FIDE codes are not ISO codes (Spain is ESP, Germany GER), so the flag needs this table.
FEDERATIONS: dict[str, tuple[str, str]] = {
    "AFG": ("Afghanistan", "AF"), "ALB": ("Albania", "AL"), "ALG": ("Algeria", "DZ"),
    "AND": ("Andorra", "AD"), "ANG": ("Angola", "AO"), "ANT": ("Antigua and Barbuda", "AG"),
    "ARG": ("Argentina", "AR"), "ARM": ("Armenia", "AM"), "ARU": ("Aruba", "AW"),
    "AUS": ("Australia", "AU"), "AUT": ("Austria", "AT"), "AZE": ("Azerbaijan", "AZ"),
    "BAH": ("Bahamas", "BS"), "BAN": ("Bangladesh", "BD"), "BAR": ("Barbados", "BB"),
    "BDI": ("Burundi", "BI"), "BEL": ("Belgium", "BE"), "BER": ("Bermuda", "BM"),
    "BHU": ("Bhutan", "BT"), "BIH": ("Bosnia and Herzegovina", "BA"), "BIZ": ("Belize", "BZ"),
    "BLR": ("Belarus", "BY"), "BOL": ("Bolivia", "BO"), "BOT": ("Botswana", "BW"),
    "BRA": ("Brazil", "BR"), "BRN": ("Bahrain", "BH"), "BRU": ("Brunei", "BN"),
    "BUL": ("Bulgaria", "BG"), "BUR": ("Burkina Faso", "BF"), "CAF": ("Central African Republic", "CF"),
    "CAM": ("Cambodia", "KH"), "CAN": ("Canada", "CA"), "CAY": ("Cayman Islands", "KY"),
    "CGO": ("Congo", "CG"), "CHA": ("Chad", "TD"), "CHI": ("Chile", "CL"), "CHN": ("China", "CN"),
    "CIV": ("Côte d'Ivoire", "CI"), "CMR": ("Cameroon", "CM"), "COD": ("DR Congo", "CD"),
    "COL": ("Colombia", "CO"), "COM": ("Comoros", "KM"), "CPV": ("Cape Verde", "CV"),
    "CRC": ("Costa Rica", "CR"), "CRO": ("Croatia", "HR"), "CUB": ("Cuba", "CU"),
    "CUR": ("Curaçao", "CW"), "CYP": ("Cyprus", "CY"), "CZE": ("Czechia", "CZ"),
    "DEN": ("Denmark", "DK"), "DJI": ("Djibouti", "DJ"), "DMA": ("Dominica", "DM"),
    "DOM": ("Dominican Republic", "DO"), "ECU": ("Ecuador", "EC"), "EGY": ("Egypt", "EG"),
    "ENG": ("England", "GB-ENG"), "ERI": ("Eritrea", "ER"), "ESA": ("El Salvador", "SV"),
    "ESP": ("Spain", "ES"), "EST": ("Estonia", "EE"), "ETH": ("Ethiopia", "ET"),
    "FAI": ("Faroe Islands", "FO"), "FID": ("FIDE", ""), "FIJ": ("Fiji", "FJ"),
    "FIN": ("Finland", "FI"), "FRA": ("France", "FR"), "GAB": ("Gabon", "GA"),
    "GAM": ("Gambia", "GM"), "GCI": ("Guernsey", "GG"), "GEO": ("Georgia", "GE"),
    "GEQ": ("Equatorial Guinea", "GQ"), "GER": ("Germany", "DE"), "GHA": ("Ghana", "GH"),
    "GRE": ("Greece", "GR"), "GRL": ("Greenland", "GL"), "GRN": ("Grenada", "GD"),
    "GUA": ("Guatemala", "GT"), "GUI": ("Guinea", "GN"), "GUM": ("Guam", "GU"),
    "GUY": ("Guyana", "GY"), "HAI": ("Haiti", "HT"), "HKG": ("Hong Kong", "HK"),
    "HON": ("Honduras", "HN"), "HUN": ("Hungary", "HU"), "INA": ("Indonesia", "ID"),
    "IND": ("India", "IN"), "IOM": ("Isle of Man", "IM"), "IRI": ("Iran", "IR"),
    "IRL": ("Ireland", "IE"), "IRQ": ("Iraq", "IQ"), "ISL": ("Iceland", "IS"),
    "ISR": ("Israel", "IL"), "ISV": ("US Virgin Islands", "VI"), "ITA": ("Italy", "IT"),
    "IVB": ("British Virgin Islands", "VG"), "JAM": ("Jamaica", "JM"), "JCI": ("Jersey", "JE"),
    "JOR": ("Jordan", "JO"), "JPN": ("Japan", "JP"), "KAZ": ("Kazakhstan", "KZ"),
    "KEN": ("Kenya", "KE"), "KGZ": ("Kyrgyzstan", "KG"), "KIR": ("Kiribati", "KI"),
    "KOR": ("South Korea", "KR"), "KOS": ("Kosovo", "XK"), "KSA": ("Saudi Arabia", "SA"),
    "KUW": ("Kuwait", "KW"), "LAO": ("Laos", "LA"), "LAT": ("Latvia", "LV"),
    "LBA": ("Libya", "LY"), "LBN": ("Lebanon", "LB"), "LBR": ("Liberia", "LR"),
    "LCA": ("Saint Lucia", "LC"), "LES": ("Lesotho", "LS"), "LIE": ("Liechtenstein", "LI"),
    "LTU": ("Lithuania", "LT"), "LUX": ("Luxembourg", "LU"), "MAC": ("Macau", "MO"),
    "MAD": ("Madagascar", "MG"), "MAR": ("Morocco", "MA"), "MAS": ("Malaysia", "MY"),
    "MAW": ("Malawi", "MW"), "MDA": ("Moldova", "MD"), "MDV": ("Maldives", "MV"),
    "MEX": ("Mexico", "MX"), "MGL": ("Mongolia", "MN"), "MKD": ("North Macedonia", "MK"),
    "MLI": ("Mali", "ML"), "MLT": ("Malta", "MT"), "MNC": ("Monaco", "MC"),
    "MNE": ("Montenegro", "ME"), "MOZ": ("Mozambique", "MZ"), "MRI": ("Mauritius", "MU"),
    "MTN": ("Mauritania", "MR"), "MYA": ("Myanmar", "MM"), "NAM": ("Namibia", "NA"),
    "NCA": ("Nicaragua", "NI"), "NCL": ("New Caledonia", "NC"), "NED": ("Netherlands", "NL"),
    "NEP": ("Nepal", "NP"), "NGR": ("Nigeria", "NG"), "NIG": ("Niger", "NE"),
    "NOR": ("Norway", "NO"), "NRU": ("Nauru", "NR"), "NZL": ("New Zealand", "NZ"),
    "OMA": ("Oman", "OM"), "PAK": ("Pakistan", "PK"), "PAN": ("Panama", "PA"),
    "PAR": ("Paraguay", "PY"), "PER": ("Peru", "PE"), "PHI": ("Philippines", "PH"),
    "PLE": ("Palestine", "PS"), "PLW": ("Palau", "PW"), "PNG": ("Papua New Guinea", "PG"),
    "POL": ("Poland", "PL"), "POR": ("Portugal", "PT"), "PUR": ("Puerto Rico", "PR"),
    "QAT": ("Qatar", "QA"), "ROU": ("Romania", "RO"), "RSA": ("South Africa", "ZA"),
    "RUS": ("Russia", "RU"), "RWA": ("Rwanda", "RW"), "SCO": ("Scotland", "GB-SCT"),
    "SEN": ("Senegal", "SN"), "SEY": ("Seychelles", "SC"), "SGP": ("Singapore", "SG"),
    "SIN": ("Singapore", "SG"), "SKN": ("Saint Kitts and Nevis", "KN"), "SLE": ("Sierra Leone", "SL"),
    "SLO": ("Slovenia", "SI"), "SMR": ("San Marino", "SM"), "SOL": ("Solomon Islands", "SB"),
    "SOM": ("Somalia", "SO"), "SRB": ("Serbia", "RS"), "SRI": ("Sri Lanka", "LK"),
    "SSD": ("South Sudan", "SS"), "STP": ("São Tomé and Príncipe", "ST"), "SUD": ("Sudan", "SD"),
    "SUI": ("Switzerland", "CH"), "SUR": ("Suriname", "SR"), "SVK": ("Slovakia", "SK"),
    "SWE": ("Sweden", "SE"), "SWZ": ("Eswatini", "SZ"), "SYR": ("Syria", "SY"),
    "TAN": ("Tanzania", "TZ"), "TGA": ("Tonga", "TO"), "THA": ("Thailand", "TH"),
    "TJK": ("Tajikistan", "TJ"), "TKM": ("Turkmenistan", "TM"), "TLS": ("Timor-Leste", "TL"),
    "TOG": ("Togo", "TG"), "TPE": ("Chinese Taipei", "TW"), "TTO": ("Trinidad and Tobago", "TT"),
    "TUN": ("Tunisia", "TN"), "TUR": ("Türkiye", "TR"), "UAE": ("United Arab Emirates", "AE"),
    "UGA": ("Uganda", "UG"), "UKR": ("Ukraine", "UA"), "URU": ("Uruguay", "UY"),
    "USA": ("United States", "US"), "UZB": ("Uzbekistan", "UZ"), "VAN": ("Vanuatu", "VU"),
    "VEN": ("Venezuela", "VE"), "VIE": ("Vietnam", "VN"), "VIN": ("St Vincent and the Grenadines", "VC"),
    "WLS": ("Wales", "GB-WLS"), "YEM": ("Yemen", "YE"), "ZAM": ("Zambia", "ZM"), "ZIM": ("Zimbabwe", "ZW"),
}


def federation_name(code: str) -> str:
    """The country name, or the code itself when FIDE uses a code not in the table."""
    return FEDERATIONS.get(code, (code, ""))[0]


def federation_flag(code: str) -> str:
    """Flag emoji for a FIDE federation code, or "" when there is none."""
    region = FEDERATIONS.get(code, ("", ""))[1]
    if not region:
        return ""
    if "-" in region:  # England, Scotland and Wales: a black flag followed by the subdivision tag
        tag = region.lower().replace("-", "")
        return "\U0001F3F4" + "".join(chr(0xE0000 + ord(c)) for c in tag) + "\U000E007F"
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in region)
