# products/management/commands/seed_categories.py
from django.core.management.base import BaseCommand
from products.models import Category

class Command(BaseCommand):
    help = 'Crée les catégories par défaut dans la base de données'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🔧 Initialisation des catégories..."))
        
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
            # Catégorie principale
            main_cat, created = Category.objects.get_or_create(name=cat_data['name'])
            if created:
                categories_created += 1
                self.stdout.write(f"✅ {cat_data['name']}")
            
            # Sous-catégories
            for subcat_name in cat_data['subcategories']:
                subcat, sub_created = Category.objects.get_or_create(
                    name=subcat_name,
                    parent=main_cat
                )
                if sub_created:
                    categories_created += 1
                    self.stdout.write(f"   ├── {subcat_name}")
        
        self.stdout.write(self.style.SUCCESS(
            f"\n✨ {categories_created} catégories créées avec succès !"
        ))
        self.stdout.write(self.style.SUCCESS(
            f"📊 Total des catégories : {Category.objects.count()}"
        ))