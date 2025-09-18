from sqlalchemy.orm import Session

def check_filters_and_notify(db: Session):
    # TODO: implémenter
    # 1) lire les filtres actifs par utilisateur
    # 2) interroger Vinted via httpx/playwright + SmartProxy
    # 3) si match -> notifier (email/push) + option sniping auto
    pass
