from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category, CategoryRule, Transaction, User
from app.services.categorization.default_rules import DEFAULT_KEYWORDS
from app.services.statements import import_statement

SAMPLE_DIR = Path(__file__).resolve().parents[3] / "sample_data"

EXPECTED = {
    "MAAŞ ÖDEMESİ - ÖRNEK TEKNOLOJİ A.Ş.": "Gelir",
    "KİRA ÖDEMESİ": "Kira",
    "MIGROS KADIKÖY İSTANBUL": "Market",
    "İSTANBULKART DOLUM": "Ulaşım",
    "STARBUCKS MODA": "Yemek",
    "NETFLIX.COM": "Abonelikler",
    "SPOTIFY": "Abonelikler",
    "SHELL KADIKÖY": "Ulaşım",
    "A101 MODA": "Market",
    "TURKCELL FATURA": "Faturalar",
    "İGDAŞ DOĞALGAZ": "Faturalar",
    "YEMEKSEPETİ": "Yemek",
    "BİM KADIKÖY": "Market",
    "ATM NAKİT ÇEKİM": "Nakit Çekim",
    "ECZANE ŞİFA": "Sağlık",
    "LC WAIKIKI": "Giyim",
    "ŞOK MARKET": "Market",
    "CINEMAXIMUM": "Eğlence",
    "TRENDYOL": "Alışveriş",
    "CK BOĞAZİÇİ ELEKTRİK": "Faturalar",
    "GETİR": "Market",
    "OPET ATAŞEHİR": "Ulaşım",
    "İSKİ SU FATURASI": "Faturalar",
    "FAİZ GELİRİ": "Gelir",
    "CARREFOURSA ATAŞEHİR": "Market",
    "YOUTUBE PREMIUM": "Abonelikler",
    "BP MASLAK": "Ulaşım",
    "GELEN HAVALE - BORÇ İADESİ": "Transfer",
    "KOTON": "Giyim",
    "AMAZON.COM.TR": "Alışveriş",
    "MIGROS SANAL MARKET": "Market",
    "PEGASUS HAVA YOLLARI": "Ulaşım",
    "DOMINOS PIZZA": "Yemek",
    "DECATHLON": "Alışveriş",
    "STEAM PURCHASE": "Eğlence",
    "ÖNCEKİ DÖNEM ÖDEMESİ": "Transfer",
    "ZARA": "Giyim",
    "TRENDYOL İADE": "Alışveriş",
    "BURGER KING": "Yemek",
    "HEPSİBURADA": "Alışveriş",
    "DİŞ HEKİMİ MUAYENE": "Sağlık",
    "APPLE.COM/BILL": "Abonelikler",
}


def import_sample(db: Session, user: User, file_name: str) -> None:
    import_statement(db, user, file_name, (SAMPLE_DIR / file_name).read_bytes())


def categories_by_description(db: Session) -> dict[str, str]:
    rows = db.execute(
        select(Transaction.description, Category.name).join(
            Category, Transaction.category_id == Category.id
        )
    )
    return {description: name for description, name in rows}


def test_every_default_keyword_category_exists(db: Session) -> None:
    seeded = set(db.scalars(select(Category.name).where(Category.user_id.is_(None))))

    assert set(DEFAULT_KEYWORDS) <= seeded


def test_sample_statements_are_categorized(db: Session, user: User) -> None:
    for file_name in (
        "ornek_hesap_ekstresi_2026_09.csv",
        "ornek_hesap_ekstresi_2026_10.pdf",
        "ornek_kredi_karti_2026_10.csv",
    ):
        import_sample(db, user, file_name)

    assert categories_by_description(db) == EXPECTED


def test_user_rule_is_applied_before_defaults_on_import(db: Session, user: User) -> None:
    hobby = Category(user_id=user.id, name="Hobi", color="#000000", icon="x")
    db.add(hobby)
    db.flush()
    db.add(CategoryRule(user_id=user.id, keyword="DECATHLON", category_id=hobby.id))
    db.flush()

    import_sample(db, user, "ornek_kredi_karti_2026_10.csv")

    assert categories_by_description(db)["DECATHLON"] == "Hobi"


def test_imported_transactions_are_not_marked_manual(db: Session, user: User) -> None:
    import_sample(db, user, "ornek_hesap_ekstresi_2026_09.csv")

    assert not any(db.scalars(select(Transaction.is_manually_categorized)))
