# products/setup_categories.py
import os
import sys
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Terrabia.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize Django
django.setup()

from products.models import Category

def create_default_categories():
    """Crée les catégories par défaut si elles n'existent pas."""
    
    default_categories = [
        {
            'name': 'Fruits',
            'subcategories': ['Agrumes', 'Fruits Rouges', 'Fruits Exotiques', 'Fruits à Noyau']
        },
        {
            'name': 'Légumes',
            'subcategories': ['Légumes Racines', 'Légumes Feuilles', 'Légumes Fruits', 'Légumes Bulbes']
        },
        {
            'name': 'Céréales et Graines',
            'subcategories': ['Riz', 'Maïs', 'Blé', 'Millet', 'Sorgho']
        },
        {
            'name': 'Tubercules',
            'subcategories': ['Manioc', 'Patate Douce', 'Igname', 'Taro']
        },
        {
            'name': 'Légumineuses',
            'subcategories': ['Haricots', 'Pois', 'Lentilles', 'Pois Chiches']
        },
        {
            'name': 'Épices et Condiments',
            'subcategories': ['Épices', 'Herbes Aromatiques', 'Assaisonnements']
        },
        {
            'name': 'Produits Animaliers',
            'subcategories': ['Œufs', 'Miel', 'Viande', 'Poisson']
        },
        {
            'name': 'Produits Transformés',
            'subcategories': ['Huiles', 'Farines', 'Conserves', 'Boissons']
        },
        {
            'name': 'Plants et Semences',
            'subcategories': ['Plants', 'Semences', 'Boutures']
        }
    ]
    
    categories_created = 0
    
    for category_data in default_categories:
        # Créer la catégorie principale
        main_category, created = Category.objects.get_or_create(
            name=category_data['name'],
            defaults={'slug': None}  # Le slug sera généré automatiquement
        )
        
        if created:
            categories_created += 1
            print(f"✅ Catégorie créée : {category_data['name']}")
        else:
            print(f"ℹ️ Catégorie déjà existante : {category_data['name']}")
        
        # Créer les sous-catégories
        for subcat_name in category_data['subcategories']:
            subcategory, sub_created = Category.objects.get_or_create(
                name=subcat_name,
                parent=main_category,
                defaults={'slug': None}
            )
            
            if sub_created:
                categories_created += 1
                print(f"   ├── Sous-catégorie créée : {subcat_name}")
    
    return categories_created

def main():
    """Fonction principale exécutée par le script."""
    print("🔧 Initialisation des catégories par défaut...")
    print("=" * 50)
    
    total_categories = create_default_categories()
    
    print("=" * 50)
    print(f"📊 Total des catégories dans la base : {Category.objects.count()}")
    print(f"✨ Catégories créées lors de cette initialisation : {total_categories}")
    print("✅ Initialisation terminée !")

if __name__ == "__main__":
    main()