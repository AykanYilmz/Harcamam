"""FAKE statements for the demo account and the files in sample_data/.

Every bank, account and transaction here is invented. May to October form one household's
history: a raise in June and in August, a summer holiday in July, balances carrying over.
"""

from decimal import Decimal

BANK = "ÖRNEK BANK A.Ş."
SEPTEMBER_OPENING = Decimal("12500")

Row = tuple[str, str, str]  # date, description, signed amount

ACCOUNT_SEPTEMBER: list[Row] = [
    ("01.09.2026", "MAAŞ ÖDEMESİ - ÖRNEK TEKNOLOJİ A.Ş.", "45000.00"),
    ("01.09.2026", "KİRA ÖDEMESİ", "-15000.00"),
    ("02.09.2026", "MIGROS KADIKÖY İSTANBUL", "-1245.80"),
    ("03.09.2026", "İSTANBULKART DOLUM", "-500.00"),
    # Two identical purchases on the same day: both are real and must both be imported.
    ("04.09.2026", "STARBUCKS MODA", "-95.00"),
    ("04.09.2026", "STARBUCKS MODA", "-95.00"),
    ("05.09.2026", "NETFLIX.COM", "-149.99"),
    ("05.09.2026", "SPOTIFY", "-59.99"),
    ("07.09.2026", "SHELL KADIKÖY", "-1850.00"),
    ("08.09.2026", "A101 MODA", "-312.45"),
    ("10.09.2026", "TURKCELL FATURA", "-429.00"),
    ("11.09.2026", "İGDAŞ DOĞALGAZ", "-684.30"),
    ("12.09.2026", "YEMEKSEPETİ", "-387.50"),
    ("14.09.2026", "BİM KADIKÖY", "-198.75"),
    ("15.09.2026", "ATM NAKİT ÇEKİM", "-2000.00"),
    ("16.09.2026", "ECZANE ŞİFA", "-146.20"),
    ("18.09.2026", "LC WAIKIKI", "-899.99"),
    ("20.09.2026", "ŞOK MARKET", "-164.90"),
    ("21.09.2026", "CINEMAXIMUM", "-340.00"),
    ("23.09.2026", "TRENDYOL", "-1129.00"),
    ("24.09.2026", "CK BOĞAZİÇİ ELEKTRİK", "-512.60"),
    ("26.09.2026", "GETİR", "-245.40"),
    ("27.09.2026", "OPET ATAŞEHİR", "-1600.00"),
    ("28.09.2026", "MIGROS KADIKÖY İSTANBUL", "-876.15"),
    ("29.09.2026", "İSKİ SU FATURASI", "-238.70"),
    ("30.09.2026", "FAİZ GELİRİ", "87.35"),
]

# May-August lead up to September: same household, a raise in June and again in August,
# and a summer holiday in July.
ACCOUNT_MAY: list[Row] = [
    ("01.05.2026", "MAAŞ ÖDEMESİ - ÖRNEK TEKNOLOJİ A.Ş.", "30000.00"),
    ("01.05.2026", "KİRA ÖDEMESİ", "-15000.00"),
    ("02.05.2026", "MIGROS KADIKÖY İSTANBUL", "-1312.40"),
    ("03.05.2026", "İSTANBULKART DOLUM", "-500.00"),
    ("05.05.2026", "NETFLIX.COM", "-149.99"),
    ("05.05.2026", "SPOTIFY", "-59.99"),
    ("06.05.2026", "SHELL KADIKÖY", "-1780.00"),
    ("08.05.2026", "KAHVE DÜNYASI MODA", "-142.00"),
    ("09.05.2026", "A101 MODA", "-284.60"),
    ("10.05.2026", "TURKCELL FATURA", "-429.00"),
    ("11.05.2026", "İGDAŞ DOĞALGAZ", "-1186.40"),
    ("13.05.2026", "YEMEKSEPETİ", "-412.00"),
    ("15.05.2026", "ATM NAKİT ÇEKİM", "-1500.00"),
    ("16.05.2026", "BİM KADIKÖY", "-176.25"),
    ("18.05.2026", "DEFACTO", "-749.97"),
    ("19.05.2026", "BERBER SALONU", "-350.00"),
    ("21.05.2026", "BİLETİX KONSER", "-1200.00"),
    ("23.05.2026", "HEPSİBURADA", "-2349.00"),
    ("24.05.2026", "CK BOĞAZİÇİ ELEKTRİK", "-468.90"),
    ("26.05.2026", "MIGROS KADIKÖY İSTANBUL", "-954.30"),
    ("27.05.2026", "OPET ATAŞEHİR", "-1650.00"),
    ("28.05.2026", "İSKİ SU FATURASI", "-226.80"),
    ("29.05.2026", "ECZANE ŞİFA", "-212.40"),
    ("31.05.2026", "FAİZ GELİRİ", "81.20"),
]

ACCOUNT_JUNE: list[Row] = [
    ("01.06.2026", "MAAŞ ÖDEMESİ - ÖRNEK TEKNOLOJİ A.Ş.", "40000.00"),
    ("01.06.2026", "KİRA ÖDEMESİ", "-15000.00"),
    ("02.06.2026", "CARREFOURSA ATAŞEHİR", "-1198.75"),
    ("03.06.2026", "İSTANBULKART DOLUM", "-500.00"),
    ("05.06.2026", "NETFLIX.COM", "-149.99"),
    ("05.06.2026", "SPOTIFY", "-59.99"),
    ("07.06.2026", "BP MASLAK", "-1820.00"),
    ("08.06.2026", "STARBUCKS MODA", "-110.00"),
    ("10.06.2026", "TURKCELL FATURA", "-429.00"),
    ("11.06.2026", "İGDAŞ DOĞALGAZ", "-542.10"),
    ("12.06.2026", "TRENDYOL YEMEK", "-365.50"),
    ("14.06.2026", "MAVİ JEANS", "-1399.90"),
    ("15.06.2026", "ATM NAKİT ÇEKİM", "-2000.00"),
    ("16.06.2026", "ŞOK MARKET", "-231.60"),
    ("17.06.2026", "KREDİ KARTI ÖDEMESİ", "-6000.00"),
    ("18.06.2026", "MEDIAMARKT", "-4299.00"),
    ("20.06.2026", "CINEMAXIMUM", "-380.00"),
    ("21.06.2026", "MIGROS KADIKÖY İSTANBUL", "-1067.85"),
    ("22.06.2026", "GELEN HAVALE - ARKADAŞ", "750.00"),
    ("24.06.2026", "CK BOĞAZİÇİ ELEKTRİK", "-531.40"),
    ("25.06.2026", "DOMINOS PIZZA", "-298.00"),
    ("27.06.2026", "SHELL KADIKÖY", "-1700.00"),
    ("28.06.2026", "İSKİ SU FATURASI", "-244.10"),
    ("30.06.2026", "FAİZ GELİRİ", "84.60"),
]

ACCOUNT_JULY: list[Row] = [
    ("01.07.2026", "MAAŞ ÖDEMESİ - ÖRNEK TEKNOLOJİ A.Ş.", "40000.00"),
    ("01.07.2026", "KİRA ÖDEMESİ", "-15000.00"),
    ("02.07.2026", "MIGROS KADIKÖY İSTANBUL", "-1405.20"),
    ("03.07.2026", "İSTANBULKART DOLUM", "-500.00"),
    ("04.07.2026", "PEGASUS HAVA YOLLARI", "-3480.00"),
    ("05.07.2026", "NETFLIX.COM", "-149.99"),
    ("05.07.2026", "SPOTIFY", "-59.99"),
    ("06.07.2026", "BOOKING.COM OTEL", "-8750.00"),
    ("10.07.2026", "TURKCELL FATURA", "-429.00"),
    ("11.07.2026", "İGDAŞ DOĞALGAZ", "-318.70"),
    ("12.07.2026", "BODRUM BALIK RESTORAN", "-1650.00"),
    ("13.07.2026", "UBER BODRUM", "-420.00"),
    ("14.07.2026", "ATM NAKİT ÇEKİM", "-3000.00"),
    ("15.07.2026", "ZARA", "-1549.95"),
    ("17.07.2026", "BİM KADIKÖY", "-205.40"),
    ("19.07.2026", "YEMEKSEPETİ", "-486.00"),
    ("21.07.2026", "OPET ATAŞEHİR", "-1750.00"),
    ("23.07.2026", "A101 MODA", "-338.15"),
    ("24.07.2026", "CK BOĞAZİÇİ ELEKTRİK", "-688.30"),
    ("26.07.2026", "MIGROS KADIKÖY İSTANBUL", "-812.65"),
    ("28.07.2026", "İSKİ SU FATURASI", "-297.50"),
    ("31.07.2026", "FAİZ GELİRİ", "79.40"),
]

ACCOUNT_AUGUST: list[Row] = [
    ("01.08.2026", "MAAŞ ÖDEMESİ - ÖRNEK TEKNOLOJİ A.Ş.", "45000.00"),
    ("01.08.2026", "KİRA ÖDEMESİ", "-15000.00"),
    ("02.08.2026", "MIGROS KADIKÖY İSTANBUL", "-1156.90"),
    ("03.08.2026", "İSTANBULKART DOLUM", "-500.00"),
    ("05.08.2026", "NETFLIX.COM", "-149.99"),
    ("05.08.2026", "SPOTIFY", "-59.99"),
    ("05.08.2026", "YOUTUBE PREMIUM", "-57.99"),
    ("07.08.2026", "SHELL KADIKÖY", "-1880.00"),
    ("09.08.2026", "SİMİT SARAYI", "-96.50"),
    ("10.08.2026", "TURKCELL FATURA", "-429.00"),
    ("11.08.2026", "İGDAŞ DOĞALGAZ", "-296.40"),
    ("13.08.2026", "GETİR", "-318.75"),
    ("14.08.2026", "IKEA ÜMRANİYE", "-3640.00"),
    ("15.08.2026", "ATM NAKİT ÇEKİM", "-1000.00"),
    ("16.08.2026", "KREDİ KARTI ÖDEMESİ", "-10000.00"),
    ("17.08.2026", "HASTANE MUAYENE", "-1250.00"),
    ("18.08.2026", "ŞOK MARKET", "-187.30"),
    ("20.08.2026", "LC WAIKIKI", "-679.99"),
    ("22.08.2026", "PLAYSTATION STORE", "-899.00"),
    ("24.08.2026", "CK BOĞAZİÇİ ELEKTRİK", "-742.80"),
    ("25.08.2026", "TRENDYOL", "-1189.00"),
    ("27.08.2026", "OPET ATAŞEHİR", "-1600.00"),
    ("28.08.2026", "İSKİ SU FATURASI", "-281.20"),
    ("29.08.2026", "MIGROS KADIKÖY İSTANBUL", "-934.55"),
    ("31.08.2026", "FAİZ GELİRİ", "83.75"),
]

# Starts on 26.09 so it overlaps the last five September transactions above.
ACCOUNT_OCTOBER: list[Row] = ACCOUNT_SEPTEMBER[-5:] + [
    ("01.10.2026", "MAAŞ ÖDEMESİ - ÖRNEK TEKNOLOJİ A.Ş.", "45000.00"),
    ("01.10.2026", "KİRA ÖDEMESİ", "-15000.00"),
    ("02.10.2026", "CARREFOURSA ATAŞEHİR", "-1432.60"),
    ("03.10.2026", "İSTANBULKART DOLUM", "-500.00"),
    ("05.10.2026", "NETFLIX.COM", "-149.99"),
    ("05.10.2026", "SPOTIFY", "-59.99"),
    ("06.10.2026", "YOUTUBE PREMIUM", "-57.99"),
    ("08.10.2026", "BP MASLAK", "-1725.00"),
    ("09.10.2026", "MIGROS KADIKÖY İSTANBUL", "-1088.40"),
    ("10.10.2026", "TURKCELL FATURA", "-429.00"),
    ("12.10.2026", "İGDAŞ DOĞALGAZ", "-912.75"),
    ("14.10.2026", "YEMEKSEPETİ", "-455.00"),
    ("15.10.2026", "GELEN HAVALE - BORÇ İADESİ", "1500.00"),
    ("17.10.2026", "A101 MODA", "-276.30"),
    ("19.10.2026", "ECZANE ŞİFA", "-89.50"),
    ("21.10.2026", "ATM NAKİT ÇEKİM", "-1000.00"),
    ("23.10.2026", "BİM KADIKÖY", "-221.10"),
    ("24.10.2026", "CK BOĞAZİÇİ ELEKTRİK", "-498.20"),
    ("26.10.2026", "SHELL KADIKÖY", "-1900.00"),
    ("28.10.2026", "KOTON", "-649.90"),
    ("29.10.2026", "İSKİ SU FATURASI", "-251.40"),
    ("31.10.2026", "FAİZ GELİRİ", "92.10"),
]

# Credit card statement: purchases in the debit column, payments/refunds in credit.
CARD_OCTOBER: list[Row] = [
    ("02.10.2026", "AMAZON.COM.TR", "-1249.00"),
    ("04.10.2026", "MIGROS SANAL MARKET", "-687.35"),
    ("07.10.2026", "PEGASUS HAVA YOLLARI", "-2340.00"),
    ("09.10.2026", "DOMINOS PIZZA", "-329.00"),
    ("11.10.2026", "DECATHLON", "-1099.00"),
    ("13.10.2026", "STEAM PURCHASE", "-214.99"),
    ("15.10.2026", "ÖNCEKİ DÖNEM ÖDEMESİ", "5000.00"),
    ("18.10.2026", "ZARA", "-1799.95"),
    ("20.10.2026", "TRENDYOL İADE", "349.00"),
    ("22.10.2026", "BURGER KING", "-265.00"),
    ("25.10.2026", "HEPSİBURADA", "-899.00"),
    ("27.10.2026", "DİŞ HEKİMİ MUAYENE", "-1500.00"),
    ("30.10.2026", "APPLE.COM/BILL", "-49.99"),
]


def tr(amount: Decimal) -> str:
    """1234.5 -> '1.234,50'"""
    return f"{amount:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def with_balances(rows: list[Row], opening: Decimal) -> list[tuple[str, str, Decimal, Decimal]]:
    balance = opening
    result = []
    for day, description, amount in rows:
        balance += Decimal(amount)
        result.append((day, description, Decimal(amount), balance))
    return result


def account_csv(rows: list[Row], period: str, opening: Decimal) -> str:
    lines = [
        f"{BANK} - HESAP HAREKETLERİ",
        "Müşteri;ÖRNEK KULLANICI",
        "IBAN;TR00 0000 0000 0000 0000 0000 00",
        f"Dönem;{period}",
        "",
        "İşlem Tarihi;Açıklama;Tutar;Bakiye",
    ]
    for day, description, amount, balance in with_balances(rows, opening):
        lines.append(f"{day};{description};{tr(amount)} TL;{tr(balance)} TL")
    return "\n".join(lines) + "\n"


def _total(rows: list[Row]) -> Decimal:
    return sum((Decimal(amount) for _, _, amount in rows), Decimal(0))


# (file name suffix, rows, period shown in the header)
ACCOUNT_MONTHS: list[tuple[str, list[Row], str]] = [
    ("2026_05", ACCOUNT_MAY, "01.05.2026 - 31.05.2026"),
    ("2026_06", ACCOUNT_JUNE, "01.06.2026 - 30.06.2026"),
    ("2026_07", ACCOUNT_JULY, "01.07.2026 - 31.07.2026"),
    ("2026_08", ACCOUNT_AUGUST, "01.08.2026 - 31.08.2026"),
    ("2026_09", ACCOUNT_SEPTEMBER, "01.09.2026 - 30.09.2026"),
]

# September opens at 12.500 TL; May opens wherever makes August end there.
MAY_OPENING = SEPTEMBER_OPENING - sum(
    (_total(rows) for _, rows, _ in ACCOUNT_MONTHS[:-1]), Decimal(0)
)
# October's statement starts on 26.09, five transactions before September's ends.
OCTOBER_OPENING = SEPTEMBER_OPENING + _total(ACCOUNT_SEPTEMBER[:-5])


def account_csvs() -> list[tuple[str, str]]:
    """(file name, CSV text) for May to September, balances carried from month to month."""
    files = []
    opening = MAY_OPENING
    for suffix, rows, period in ACCOUNT_MONTHS:
        files.append((f"ornek_hesap_ekstresi_{suffix}.csv", account_csv(rows, period, opening)))
        opening += _total(rows)
    return files


def card_csv() -> str:
    """October's credit card statement, with separate debit and credit columns."""
    lines = [
        f"{BANK} KREDİ KARTI EKSTRESİ",
        "Kart No;**** **** **** 0000",
        "Hesap Kesim Tarihi;31.10.2026",
        "",
        "TARİH;AÇIKLAMA;BORÇ;ALACAK",
    ]
    for day, description, amount in CARD_OCTOBER:
        value = Decimal(amount)
        debit, credit = (tr(-value), "") if value < 0 else ("", tr(value))
        lines.append(f"{day};{description};{debit};{credit}")
    return "\n".join(lines) + "\n"
