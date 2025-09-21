from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.filter import VintedFilter
from ..models.alert import Alert
from .vinted_scraper import VintedScraper

async def check_filters_and_notify(db: Session):
    """Vérifie tous les filtres actifs et envoie des notifications"""
    
    # Récupère tous les filtres actifs
    active_filters = db.query(VintedFilter).filter(VintedFilter.is_active == True).all()
    
    # Pour chaque filtre, lance le scraping
    for filter_obj in active_filters:
        try:
            async with VintedScraper() as scraper:
                items = await scraper.search_items(
                    filters={
                        'category': filter_obj.category,
                        'brand': filter_obj.brand,
                        'min_price': filter_obj.min_price,
                        'max_price': filter_obj.max_price,
                        'keywords': filter_obj.keywords
                    },
                    user_id=filter_obj.user_id
                )
                
                # Traite les résultats et crée des alertes
                for item in items:
                    # Vérifie si l'alerte existe déjà
                    existing_alert = db.query(Alert).filter(
                        Alert.filter_id == filter_obj.id,
                        Alert.vinted_item_id == item['id']
                    ).first()
                    
                    if not existing_alert:
                        # Crée une nouvelle alerte
                        alert = Alert(
                            user_id=filter_obj.user_id,
                            filter_id=filter_obj.id,
                            vinted_item_id=item['id'],
                            item_title=item['title'],
                            item_price=item['price'],
                            item_url=item['url']
                        )
                        db.add(alert)
                        
        except Exception as e:
            print(f"Erreur pour filtre {filter_obj.id}: {e}")
            continue
    
    db.commit()
