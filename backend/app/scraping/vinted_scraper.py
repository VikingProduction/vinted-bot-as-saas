"""
Scraper Vinted avec SmartProxy et contournement anti-bot
"""
import asyncio
import httpx
import random
import json
import time
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urlencode
from ..core.config import settings, logger
from ..proxy_manager import ProxyManager  # Le fichier est à la racine de app/
from .anti_bot import AntiBot


class VintedScraper:
    """Scraper principal pour Vinted avec gestion SmartProxy"""
    
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.anti_bot = AntiBot()
        self.session = None
        self.base_url = "https://www.vinted.fr"
        self.api_base = "https://www.vinted.fr/api/v2"
        self.request_count = 0
        self.last_rotation = datetime.now()
        
    async def __aenter__(self):
        """Initialisation de la session avec SmartProxy"""
        proxy_config = self.proxy_manager.get_proxy_config()
        
        self.session = httpx.AsyncClient(
            proxies=proxy_config,
            timeout=30.0,
            headers=self.anti_bot.get_headers(),
            follow_redirects=True
        )
        
        logger.info("✅ Session Vinted scraper initialisée avec SmartProxy")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
            logger.info("🛑 Session Vinted scraper fermée")
    
    async def search_items(self, filters: Dict, user_id: int = None) -> List[Dict]:
        """
        Recherche d'articles selon les filtres donnés
        
        Args:
            filters: Dictionnaire des filtres de recherche
            user_id: ID utilisateur pour tracking
            
        Returns:
            Liste des articles trouvés
        """
        try:
            # Rotation de proxy si nécessaire
            await self._check_rotation_needed()
            
            # Construction de l'URL de recherche
            search_url = self._build_search_url(filters)
            
            # Délai anti-détection
            await self._apply_human_delay()
            
            # Requête avec gestion d'erreurs
            response = await self._make_request(search_url, user_id)
            
            if not response:
                return []
            
            # Parsing des résultats
            items = self._parse_search_results(response.text, response.headers.get('content-type', ''))
            
            logger.info(
                "🔍 Recherche terminée",
                user_id=user_id,
                filters_count=len(filters),
                items_found=len(items),
                request_count=self.request_count
            )
            
            return items
            
        except Exception as e:
            logger.error(
                "❌ Erreur lors du scraping",
                user_id=user_id,
                error=str(e),
                filters=filters
            )
            return []
    
    def _build_search_url(self, filters: Dict) -> str:
        """Construction de l'URL de recherche avec filtres"""
        
        # Paramètres de base
        params = {
            'time': int(time.time()),  # Cache busting
            'per_page': 96,  # Maximum d'articles par page
            'order': 'newest_first'  # Tri par plus récent
        }
        
        # Mapping des filtres Vinted
        filter_mapping = {
            'category_id': self._get_category_id(filters.get('category')),
            'brand_ids[]': self._get_brand_ids(filters.get('brands', [])),
            'size_ids[]': self._get_size_ids(filters.get('sizes', [])),
            'color_ids[]': self._get_color_ids(filters.get('colors', [])),
            'material_ids[]': self._get_material_ids(filters.get('materials', [])),
            'status_ids[]': self._get_status_ids(filters.get('conditions', [])),
            'price_from': filters.get('min_price'),
            'price_to': filters.get('max_price'),
            'currency': 'EUR'
        }
        
        # Ajout des filtres valides
        for key, value in filter_mapping.items():
            if value is not None:
                if isinstance(value, list):
                    for v in value:
                        params[key] = v
                else:
                    params[key] = value
        
        # Mots-clés dans le titre
        if filters.get('keywords'):
            params['search_text'] = filters['keywords']
        
        # URL finale
        query_string = urlencode(params, doseq=True)
        return f"{self.api_base}/catalog/items?{query_string}"
    
    async def _make_request(self, url: str, user_id: int = None) -> Optional[httpx.Response]:
        """Effectue une requête HTTP avec gestion d'erreurs"""
        
        try:
            # Headers spécifiques pour cette requête
            headers = self.anti_bot.get_headers()
            headers.update({
                'Referer': 'https://www.vinted.fr/',
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json, text/plain, */*'
            })
            
            response = await self.session.get(url, headers=headers)
            self.request_count += 1
            
            # Gestion des codes d'erreur
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                logger.warning("⚠️ Rate limit détecté", user_id=user_id)
                await self._handle_rate_limit()
                return None
            elif response.status_code == 403:
                logger.warning("🚫 Accès interdit (anti-bot?)", user_id=user_id)
                await self._handle_bot_detection()
                return None
            else:
                logger.warning(
                    "⚠️ Code de réponse inattendu",
                    status_code=response.status_code,
                    user_id=user_id
                )
                return None
                
        except httpx.TimeoutException:
            logger.warning("⏱️ Timeout de requête", user_id=user_id)
            return None
        except Exception as e:
            logger.error("❌ Erreur requête HTTP", error=str(e), user_id=user_id)
            return None
    
    def _parse_search_results(self, content: str, content_type: str) -> List[Dict]:
        """Parse les résultats de recherche selon le type de contenu"""
        
        try:
            # Tentative de parsing JSON (API)
            if 'application/json' in content_type:
                data = json.loads(content)
                if 'items' in data:
                    return self._format_api_results(data['items'])
            
            # Fallback parsing HTML
            soup = BeautifulSoup(content, 'html.parser')
            return self._parse_html_results(soup)
            
        except json.JSONDecodeError:
            logger.warning("⚠️ Erreur parsing JSON, tentative HTML")
            soup = BeautifulSoup(content, 'html.parser')
            return self._parse_html_results(soup)
        except Exception as e:
            logger.error("❌ Erreur parsing résultats", error=str(e))
            return []
    
    def _format_api_results(self, items: List[Dict]) -> List[Dict]:
        """Formatage des résultats API Vinted"""
        
        formatted_items = []
        
        for item in items:
            try:
                formatted_item = {
                    'id': str(item.get('id')),
                    'title': item.get('title', ''),
                    'price': float(item.get('price', {}).get('amount', 0)),
                    'currency': item.get('price', {}).get('currency_code', 'EUR'),
                    'size': item.get('size_title', ''),
                    'brand': item.get('brand_title', ''),
                    'condition': item.get('status', ''),
                    'url': f"{self.base_url}/items/{item.get('id')}",
                    'photo_url': self._get_photo_url(item.get('photos', [])),
                    'user': {
                        'id': item.get('user', {}).get('id'),
                        'username': item.get('user', {}).get('login'),
                    },
                    'location': item.get('user', {}).get('city'),
                    'created_at': item.get('created_at_ts'),
                    'updated_at': item.get('updated_at_ts'),
                    'scraped_at': datetime.now().isoformat(),
                    'is_visible': item.get('is_visible', True),
                    'can_buy': not item.get('is_reserved', False)
                }
                
                formatted_items.append(formatted_item)
                
            except Exception as e:
                logger.warning("⚠️ Erreur formatage item", item_id=item.get('id'), error=str(e))
                continue
        
        return formatted_items
    
    def _parse_html_results(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse HTML si l'API n'est pas disponible"""
        
        items = []
        
        # Sélecteurs pour les éléments d'articles
        item_selectors = [
            '.feed-grid__item',
            '.item-box',
            '[data-testid="item"]'
        ]
        
        for selector in item_selectors:
            elements = soup.select(selector)
            if elements:
                break
        
        for element in elements:
            try:
                item_data = self._extract_item_from_html(element)
                if item_data:
                    items.append(item_data)
            except Exception as e:
                logger.warning("⚠️ Erreur extraction HTML item", error=str(e))
                continue
        
        return items
    
    def _extract_item_from_html(self, element) -> Optional[Dict]:
        """Extraction des données d'un article depuis HTML"""
        
        try:
            # ID de l'article
            item_id = element.get('data-item-id') or element.get('data-testid-item-id')
            
            # Titre
            title_selectors = ['[data-testid="item-title"]', '.item-title', 'h3']
            title = self._extract_text_by_selectors(element, title_selectors)
            
            # Prix
            price_selectors = ['[data-testid="item-price"]', '.item-price', '.price']
            price_text = self._extract_text_by_selectors(element, price_selectors)
            price = self._extract_price(price_text)
            
            # URL
            link = element.find('a')
            url = link['href'] if link else ""
            if url and not url.startswith('http'):
                url = self.base_url + url
            
            # Image
            img_selectors = ['img[data-testid="item-photo"]', '.item-photo img', 'img']
            img_element = element.select_one(','.join(img_selectors))
            photo_url = img_element.get('src') or img_element.get('data-src') if img_element else ""
            
            # Marque et taille
            brand_selectors = ['[data-testid="item-brand"]', '.item-brand']
            brand = self._extract_text_by_selectors(element, brand_selectors)
            
            size_selectors = ['[data-testid="item-size"]', '.item-size']
            size = self._extract_text_by_selectors(element, size_selectors)
            
            if not all([item_id, title, url]):
                return None
            
            return {
                'id': item_id,
                'title': title,
                'price': price,
                'currency': 'EUR',
                'size': size,
                'brand': brand,
                'url': url,
                'photo_url': photo_url,
                'scraped_at': datetime.now().isoformat(),
                'source': 'html_parsing'
            }
            
        except Exception as e:
            logger.warning("⚠️ Erreur extraction item HTML", error=str(e))
            return None
    
    async def get_item_details(self, item_id: str) -> Optional[Dict]:
        """Récupère les détails complets d'un article"""
        
        try:
            url = f"{self.api_base}/items/{item_id}"
            
            await self._apply_human_delay()
            response = await self._make_request(url)
            
            if not response:
                return None
            
            data = response.json()
            item = data.get('item', {})
            
            # Détails complets
            details = {
                'id': str(item.get('id')),
                'title': item.get('title'),
                'description': item.get('description'),
                'price': float(item.get('price', {}).get('amount', 0)),
                'currency': item.get('price', {}).get('currency_code', 'EUR'),
                'brand': item.get('brand_title'),
                'size': item.get('size_title'),
                'condition': item.get('status'),
                'material': item.get('material'),
                'color': item.get('color1'),
                'measurements': self._extract_measurements(item.get('item_details', [])),
                'photos': [photo.get('url') for photo in item.get('photos', [])],
                'user': {
                    'id': item.get('user', {}).get('id'),
                    'username': item.get('user', {}).get('login'),
                    'rating': item.get('user', {}).get('feedback_reputation'),
                    'items_count': item.get('user', {}).get('item_count')
                },
                'created_at': item.get('created_at_ts'),
                'updated_at': item.get('updated_at_ts'),
                'is_reserved': item.get('is_reserved', False),
                'is_visible': item.get('is_visible', True),
                'view_count': item.get('view_count', 0),
                'favourite_count': item.get('favourite_count', 0)
            }
            
            return details
            
        except Exception as e:
            logger.error("❌ Erreur récupération détails item", item_id=item_id, error=str(e))
            return None
    
    async def attempt_purchase(self, item_id: str, max_price: float, user_vinted_session: str) -> Dict:
        """
        Tentative d'achat automatique (snipping)
        
        Args:
            item_id: ID de l'article
            max_price: Prix maximum accepté
            user_vinted_session: Session Vinted de l'utilisateur
            
        Returns:
            Résultat de la tentative d'achat
        """
        
        if not settings.snipping_enabled:
            return {"success": False, "error": "Snipping désactivé"}
        
        try:
            # Vérification du prix actuel
            item_details = await self.get_item_details(item_id)
            
            if not item_details:
                return {"success": False, "error": "Article non trouvé"}
            
            if item_details['price'] > max_price:
                return {
                    "success": False, 
                    "error": f"Prix trop élevé: {item_details['price']}€ > {max_price}€"
                }
            
            if item_details['is_reserved']:
                return {"success": False, "error": "Article déjà réservé"}
            
            # Tentative d'achat avec session utilisateur
            purchase_result = await self._execute_purchase(item_id, user_vinted_session)
            
            return purchase_result
            
        except Exception as e:
            logger.error("❌ Erreur tentative achat", item_id=item_id, error=str(e))
            return {"success": False, "error": f"Erreur technique: {str(e)}"}
    
    async def _execute_purchase(self, item_id: str, user_session: str) -> Dict:
        """Exécute l'achat via l'API Vinted (simulation)"""
        
        # TODO: Implémenter la logique d'achat réelle
        # Cela nécessite:
        # 1. Authentification avec la session utilisateur
        # 2. Création d'une conversation avec le vendeur
        # 3. Proposition d'achat
        # 4. Confirmation de l'achat
        
        logger.warning("⚠️ Achat automatique non implémenté (simulation)", item_id=item_id)
        
        # Simulation d'un achat réussi (à remplacer par la vraie logique)
        await asyncio.sleep(random.uniform(1, 3))
        
        return {
            "success": True,
            "item_id": item_id,
            "action": "simulated_purchase",
            "timestamp": datetime.now().isoformat(),
            "warning": "Achat simulé - implémentation requise"
        }
    
    # Méthodes utilitaires
    
    async def _check_rotation_needed(self):
        """Vérifie si une rotation de proxy est nécessaire"""
        
        time_since_rotation = datetime.now() - self.last_rotation
        
        if (self.request_count >= 50 or 
            time_since_rotation > timedelta(minutes=30)):
            
            logger.info("🔄 Rotation de proxy nécessaire")
            await self._rotate_proxy()
    
    async def _rotate_proxy(self):
        """Effectue une rotation de proxy"""
        
        try:
            # Fermeture de l'ancienne session
            if self.session:
                await self.session.aclose()
            
            # Nouvelle configuration proxy
            proxy_config = self.proxy_manager.get_proxy_config()
            
            # Nouvelle session
            self.session = httpx.AsyncClient(
                proxies=proxy_config,
                timeout=30.0,
                headers=self.anti_bot.get_headers(),
                follow_redirects=True
            )
            
            # Reset compteurs
            self.request_count = 0
            self.last_rotation = datetime.now()
            
            # Attente stabilisation
            await asyncio.sleep(random.uniform(5, 10))
            
            logger.info("✅ Rotation de proxy terminée")
            
        except Exception as e:
            logger.error("❌ Erreur rotation proxy", error=str(e))
    
    async def _apply_human_delay(self):
        """Applique un délai humain entre les requêtes"""
        delay = random.uniform(settings.scraping_delay_min, settings.scraping_delay_max)
        await asyncio.sleep(delay)
    
    async def _handle_rate_limit(self):
        """Gestion du rate limiting"""
        
        logger.warning("⚠️ Rate limit détecté - attente et rotation")
        
        # Attente avec backoff exponentiel
        wait_time = min(300, 30 * (2 ** min(3, self.request_count // 100)))
        await asyncio.sleep(wait_time)
        
        # Rotation de proxy
        await self._rotate_proxy()
    
    async def _handle_bot_detection(self):
        """Gestion de la détection de bot"""
        
        logger.warning("🚫 Détection de bot - rotation complète")
        
        # Rotation immédiate
        await self._rotate_proxy()
        
        # Nouveau set de headers
        self.anti_bot.rotate_fingerprint()
        
        # Attente plus longue
        await asyncio.sleep(random.uniform(60, 120))
    
    # Méthodes de mapping des filtres (à compléter selon l'API Vinted)
    
    def _get_category_id(self, category: str) -> Optional[int]:
        """Mapping des catégories vers les IDs Vinted"""
        category_mapping = {
            'women': 1,
            'men': 2,
            'kids': 3,
            'home': 4,
            'entertainment': 5
        }
        return category_mapping.get(category)
    
    def _get_brand_ids(self, brands: List[str]) -> List[int]:
        """Mapping des marques vers les IDs Vinted"""
        # TODO: Implémenter le mapping complet des marques
        brand_mapping = {
            'zara': 53,
            'h&m': 49,
            'nike': 88,
            'adidas': 14
        }
        return [brand_mapping.get(brand.lower()) for brand in brands if brand.lower() in brand_mapping]
    
    def _get_size_ids(self, sizes: List[str]) -> List[int]:
        """Mapping des tailles vers les IDs Vinted"""
        # TODO: Implémenter le mapping complet des tailles
        return []
    
    def _get_color_ids(self, colors: List[str]) -> List[int]:
        """Mapping des couleurs vers les IDs Vinted"""
        # TODO: Implémenter le mapping complet des couleurs
        return []
    
    def _get_material_ids(self, materials: List[str]) -> List[int]:
        """Mapping des matières vers les IDs Vinted"""
        # TODO: Implémenter le mapping complet des matières
        return []
    
    def _get_status_ids(self, conditions: List[str]) -> List[int]:
        """Mapping des conditions vers les IDs Vinted"""
        status_mapping = {
            'new_with_tags': 6,
            'new_without_tags': 1,
            'very_good': 2,
            'good': 3,
            'satisfactory': 4
        }
        return [status_mapping.get(condition) for condition in conditions if condition in status_mapping]
    
    def _get_photo_url(self, photos: List[Dict]) -> str:
        """Récupère l'URL de la première photo"""
        if photos and len(photos) > 0:
            return photos[0].get('url', '')
        return ''
    
    def _extract_price(self, price_text: str) -> float:
        """Extrait le prix depuis le texte"""
        if not price_text:
            return 0.0
        
        # Extraction du nombre
        import re
        price_match = re.search(r'(\d+(?:,\d+)?)', price_text.replace(' ', ''))
        if price_match:
            return float(price_match.group(1).replace(',', '.'))
        return 0.0
    
    def _extract_text_by_selectors(self, element, selectors: List[str]) -> str:
        """Extrait le texte en testant plusieurs sélecteurs"""
        for selector in selectors:
            found = element.select_one(selector)
            if found:
                return found.get_text(strip=True)
        return ''
    
    def _extract_measurements(self, item_details: List[Dict]) -> Dict:
        """Extrait les mesures depuis les détails"""
        measurements = {}
        for detail in item_details:
            if detail.get('title') and detail.get('value'):
                measurements[detail['title']] = detail['value']
        return measurements
