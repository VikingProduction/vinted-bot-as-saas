"""
Configuration de base de données avec SQLAlchemy
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import redis
from typing import Generator

from .config import settings, logger

# Configuration moteur SQLAlchemy
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.debug,  # Log SQL queries en mode debug
    echo_pool=settings.debug,
    connect_args={
        "charset": "utf8mb4",
        "connect_timeout": 30,
        "read_timeout": 30,
        "write_timeout": 30,
    }
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Base pour les modèles
Base = declarative_base()

# Metadata pour les migrations
metadata = MetaData()

# Configuration Redis
redis_client = redis.from_url(
    settings.redis_url,
    password=settings.redis_password if settings.redis_password else None,
    decode_responses=True,
    retry_on_timeout=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    health_check_interval=30
)


def get_db() -> Generator[Session, None, None]:
    """
    Générateur de session de base de données pour l'injection de dépendances FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Erreur base de données", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()


def get_redis() -> redis.Redis:
    """
    Retourne le client Redis
    """
    return redis_client


def init_db():
    """
    Initialise la base de données en créant toutes les tables
    """
    try:
        # Import de tous les modèles pour créer les tables
        from .models import user, filter, alert, subscription
        
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Base de données initialisée")
        
    except Exception as e:
        logger.error("❌ Erreur initialisation base de données", error=str(e))
        raise


def check_db_connection():
    """
    Vérifie la connexion à la base de données
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logger.error("❌ Connexion base de données échouée", error=str(e))
        return False


def check_redis_connection():
    """
    Vérifie la connexion à Redis
    """
    try:
        redis_client.ping()
        return True
    except Exception as e:
        logger.error("❌ Connexion Redis échouée", error=str(e))
        return False


# Utilitaires pour les transactions
class DatabaseManager:
    """Gestionnaire de base de données avec gestion automatique des transactions"""
    
    def __init__(self):
        self.db = None
    
    def __enter__(self):
        self.db = SessionLocal()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.rollback()
            logger.error(
                "Transaction rollback", 
                error=str(exc_val), 
                type=str(exc_type)
            )
        else:
            try:
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                logger.error("Erreur commit transaction", error=str(e))
                raise
        finally:
            self.db.close()


# Cache Redis avec helpers
class CacheManager:
    """Gestionnaire de cache Redis avec helpers"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def get(self, key: str):
        """Récupère une valeur du cache"""
        try:
            return self.redis.get(key)
        except Exception as e:
            logger.warning(f"Erreur lecture cache {key}", error=str(e))
            return None
    
    def set(self, key: str, value: str, expire: int = 3600):
        """Stocke une valeur dans le cache"""
        try:
            return self.redis.setex(key, expire, value)
        except Exception as e:
            logger.warning(f"Erreur écriture cache {key}", error=str(e))
            return False
    
    def delete(self, key: str):
        """Supprime une clé du cache"""
        try:
            return self.redis.delete(key)
        except Exception as e:
            logger.warning(f"Erreur suppression cache {key}", error=str(e))
            return False
    
    def exists(self, key: str):
        """Vérifie si une clé existe dans le cache"""
        try:
            return self.redis.exists(key)
        except Exception as e:
            logger.warning(f"Erreur vérification cache {key}", error=str(e))
            return False
    
    def increment(self, key: str, amount: int = 1):
        """Incrémente une valeur numérique"""
        try:
            return self.redis.incrby(key, amount)
        except Exception as e:
            logger.warning(f"Erreur incrémentation cache {key}", error=str(e))
            return None
    
    def get_user_cache_key(self, user_id: int, suffix: str = ""):
        """Génère une clé de cache pour un utilisateur"""
        return f"user:{user_id}:{suffix}" if suffix else f"user:{user_id}"
    
    def get_filter_cache_key(self, filter_id: int, suffix: str = ""):
        """Génère une clé de cache pour un filtre"""
        return f"filter:{filter_id}:{suffix}" if suffix else f"filter:{filter_id}"


# Instance globale du gestionnaire de cache
cache_manager = CacheManager(redis_client)


# Utilitaires pour les requêtes communes
class QueryHelper:
    """Helpers pour requêtes communes"""
    
    @staticmethod
    def get_active_users(db: Session):
        """Récupère les utilisateurs actifs"""
        from .models.user import User
        return db.query(User).filter(User.is_active == True).all()
    
    @staticmethod
    def get_user_active_filters(db: Session, user_id: int):
        """Récupère les filtres actifs d'un utilisateur"""
        from .models.filter import VintedFilter
        return db.query(VintedFilter).filter(
            VintedFilter.user_id == user_id,
            VintedFilter.is_active == True
        ).all()
    
    @staticmethod
    def get_recent_alerts(db: Session, user_id: int, limit: int = 50):
        """Récupère les alertes récentes d'un utilisateur"""
        from .models.alert import Alert
        return db.query(Alert).filter(
            Alert.user_id == user_id
        ).order_by(Alert.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_user_subscription(db: Session, user_id: int):
        """Récupère l'abonnement actif d'un utilisateur"""
        from .models.subscription import Subscription
        return db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == 'active'
        ).first()


# Instance globale des helpers
query_helper = QueryHelper()


# Événements de cycle de vie de l'application
async def startup_database():
    """Initialisation de la base de données au démarrage"""
    logger.info("🔄 Initialisation base de données...")
    
    # Vérification connexion MySQL
    if not check_db_connection():
        raise Exception("Connexion MySQL impossible")
    
    # Vérification connexion Redis  
    if not check_redis_connection():
        raise Exception("Connexion Redis impossible")
    
    # Initialisation des tables
    init_db()
    
    logger.info("✅ Base de données prête")


async def shutdown_database():
    """Nettoyage au shutdown"""
    logger.info("🔄 Fermeture connexions base de données...")
    
    try:
        # Fermeture pool de connexions
        engine.dispose()
        
        # Fermeture connexions Redis
        redis_client.close()
        
        logger.info("✅ Connexions fermées proprement")
        
    except Exception as e:
        logger.error("❌ Erreur fermeture connexions", error=str(e))


# Décorateur pour les opérations avec retry
import functools
import time
from typing import Callable, Any

def db_retry(max_attempts: int = 3, delay: float = 1.0):
    """
    Décorateur pour retry automatique des opérations base de données
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"Tentative {attempt + 1}/{max_attempts} échouée",
                        function=func.__name__,
                        error=str(e)
                    )
                    
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (2 ** attempt))  # Backoff exponentiel
            
            # Si toutes les tentatives échouent
            logger.error(
                f"Toutes les tentatives échouées pour {func.__name__}",
                error=str(last_exception)
            )
            raise last_exception
        
        return wrapper
    return decorator