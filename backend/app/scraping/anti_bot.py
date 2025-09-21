import random
from fake_useragent import UserAgent
from typing import Dict

class AntiBot:
    """Classe pour contourner la détection de bots"""
    
    def __init__(self):
        self.ua = UserAgent()
    
    def get_headers(self) -> Dict[str, str]:
        """Génère des headers HTTP réalistes"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'DNT': '1'
        }
    
    def rotate_fingerprint(self):
        """Génère une nouvelle empreinte digitale"""
        # Réinitialise le user agent
        self.ua = UserAgent()
