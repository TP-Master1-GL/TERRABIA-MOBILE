# products/apps.py
from django.apps import AppConfig

class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'
    
    def ready(self):
        """
        Code exécuté lorsque l'application est prête.
        """
        import os
        
        # S'exécuter uniquement lors du démarrage du serveur principal
        if os.environ.get('RUN_MAIN') == 'true':
            try:
                self._create_default_categories()
            except Exception as e:
                print(f"⚠️ Erreur lors de l'initialisation : {e}")
    
    def _create_default_categories(self):
        """Crée les catégories par défaut si elles n'existent pas déjà."""
        from django.db.utils import OperationalError, ProgrammingError
        
        try:
            from .models import Category
            
            # Vérifier d'abord si la table existe
            try:
                # Simple test pour vérifier que la table existe
                Category.objects.first()
            except (OperationalError, ProgrammingError):
                print("📋 Table des catégories non créée. Exécutez les migrations d'abord.")
                return
            
            print("📊 Vérification et création des catégories par défaut...")
            
            default_categories = [
                {'name': 'Fruits', 'subcategories': ['Agrumes', 'Fruits Rouges', 'Fruits Exotiques']},
                {'name': 'Légumes', 'subcategories': ['Légumes Racines', 'Légumes Feuilles', 'Légumes Fruits']},
                {'name': 'Céréales', 'subcategories': ['Riz', 'Maïs', 'Blé', 'Millet']},
                {'name': 'Tubercules', 'subcategories': ['Manioc', 'Patate Douce', 'Igname']},
                {'name': 'Légumineuses', 'subcategories': ['Haricots', 'Pois', 'Lentilles']},
                {'name': 'Épices', 'subcategories': ['Épices', 'Herbes Aromatiques']},
                {'name': 'Produits Animaliers', 'subcategories': ['Œufs', 'Miel']},
            ]
            
            categories_created = 0
            
            for cat_data in default_categories:
                # Catégorie principale - vérifier si elle existe déjà
                try:
                    # Utiliser get_or_create pour éviter les doublons
                    main_cat, created = Category.objects.get_or_create(
                        name=cat_data['name']
                    )
                    if created:
                        categories_created += 1
                        print(f"✅ {cat_data['name']}")
                    else:
                        print(f"ℹ️ Catégorie déjà existante : {cat_data['name']}")
                    
                    # Sous-catégories
                    for subcat_name in cat_data['subcategories']:
                        try:
                            # Vérifier si la sous-catégorie existe déjà avec ce parent
                            subcat, sub_created = Category.objects.get_or_create(
                                name=subcat_name,
                                parent=main_cat
                            )
                            if sub_created:
                                categories_created += 1
                                print(f"   ├── {subcat_name}")
                        except Exception as e:
                            print(f"   ├── ⚠️ '{subcat_name}' : {str(e)[:50]}...")
                            
                except Exception as e:
                    print(f"⚠️ Erreur avec '{cat_data['name']}' : {str(e)[:50]}...")
                    continue
            
            if categories_created > 0:
                print(f"✨ {categories_created} nouvelles catégories créées.")
            else:
                print("✅ Toutes les catégories par défaut sont déjà présentes.")
                
        except (OperationalError, ProgrammingError) as e:
            print(f"📋 Base de données non prête : {e}")
        except Exception as e:
            print(f"⚠️ Erreur générale : {e}")