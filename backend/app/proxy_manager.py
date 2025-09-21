"""
Gestionnaire de proxies SmartProxy pour rotation intelligente
"""
import random
import time
from typing import Dict, Optional
import base64

from ..config import settings, logger


class ProxyManager:
    """Gestionnaire des proxies SmartProxy avec rotation intelligente"""
    
    def __init__(self):
        self.endpoint = settings.smartproxy_endpoint
        self.username = settings.smartproxy_username
        self.password = settings.smartproxy_password
        self.current_session = None
        self.session_start = time.time()
        self.countries = ['FR', 'DE', 'ES', 'IT', 'BE']  # Pays européens
        self.cities = ['paris', 'lyon', 'marseille', 'bordeaux']  # Villes françaises
        
    def get_proxy_config(self, force_new_session: bool = False) -> Dict[str, str]:
        """
        Retourne la configuration proxy pour httpx
        
        Args:
            force_new_session: Force une nouvelle session
            
        Returns:
            Configuration proxy pour httpx
        """
        
        # Génération nouvelle session si nécessaire
        if force_new_session or self._should_rotate_session():
            self._generate_new_session()
        
        # Configuration du proxy avec authentification
        proxy_url = f"http://{self.username}:{self.password}@{self.endpoint}"
        
        return {
            "http://": proxy_url,
            "https://": proxy_url
        }
    
    def get_proxy_headers(self) -> Dict[str, str]:
        """Retourne les headers spécifiques au proxy"""
        
        headers = {}
        
        # Session sticky pour cohérence
        if self.current_session:
            headers['Proxy-Authorization'] = self._get_auth_header()
            headers['X-SmartProxy-Session'] = self.current_session
        
        return headers
    
    def _should_rotate_session(self) -> bool:
        """Détermine si la session doit être rotée"""
        
        # Rotation toutes les 30 minutes minimum
        time_elapsed = time.time() - self.session_start
        if time_elapsed > 1800:  # 30 minutes
            return True
        
        # Rotation aléatoire pour éviter les patterns
        if random.random() < 0.1:  # 10% de chance
            return True
            
        return False
    
    def _generate_new_session(self):
        """Génère une nouvelle session avec paramètres aléatoires"""
        
        # ID de session unique basé sur timestamp + random
        session_id = f"vinted_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Sélection pays/ville aléatoire
        country = random.choice(self.countries)
        city = random.choice(self.cities) if country == 'FR' else None
        
        # Construction de la session
        session_params = [session_id]
        
        if country:
            session_params.append(f"country-{country}")
        
        if city:
            session_params.append(f"city-{city}")
        
        # Rotation de la durée de session (1h à 24h)
        session_duration = random.choice(['1h', '6h', '12h', '24h'])
        session_params.append(f"sessionduration-{session_duration}")
        
        self.current_session = "_".join(session_params)
        self.session_start = time.time()
        
        logger.info(
            "🔄 Nouvelle session SmartProxy générée",
            session=self.current_session,
            country=country,
            city=city,
            duration=session_duration
        )
    
    def _get_auth_header(self) -> str:
        """Génère le header d'authentification proxy"""
        auth_string = f"{self.username}:{self.password}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        return f"Basic {auth_b64}"
    
    def rotate_session(self):
        """Force la rotation de session"""
        self._generate_new_session()
        logger.info("✅ Session SmartProxy rotée manuellement")
    
    def get_session_info(self) -> Dict:
        """Retourne les informations de la session actuelle"""
        return {
            "session": self.current_session,
            "started_at": self.session_start,
            "age_seconds": int(time.time() - self.session_start),
            "endpoint": self.endpoint
        }
    
    def test_proxy_connection(self) -> bool:
        """Test de connectivité du proxy"""
        try:
            import httpx
            
            proxy_config = self.get_proxy_config()
            
            with httpx.Client(proxies=proxy_config, timeout=10.0) as client:
                response = client.get("https://httpbin.org/ip")
                
                if response.status_code == 200:
                    ip_info = response.json()
                    logger.info("✅ Test proxy réussi", ip=ip_info.get('origin'))
                    return True
                else:
                    logger.error("❌ Test proxy échoué", status=response.status_code)
                    return False
                    
        except Exception as e:
            logger.error("❌ Erreur test proxy", error=str(e))
            return False
