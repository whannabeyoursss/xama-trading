from django.db import migrations, models


def seed_products(apps, schema_editor):
    Category = apps.get_model('core', 'Category')
    Product = apps.get_model('core', 'Product')

    seasoning, _ = Category.objects.get_or_create(name='Seasoning')
    beverages, _ = Category.objects.get_or_create(name='Beverages')

    products = [
        {
            'name': 'MAGIC SARAP 8G PACK OF 12 SACHETS',
            'sku': 'MAGIC-SARAP-8G-12',
            'category': seasoning,
            'description': 'Magic Sarap 8g pack of 12 sachets.',
            'image': 'core/products/magic-sarap.png',
            'price': 35,
            'quantity': 100,
            'reorder_level': 12,
        },
        {
            'name': 'VETSIN 11G PER PACK 18 SACHETS',
            'sku': 'VETSIN-11G-18',
            'category': seasoning,
            'description': 'Vetsin 11g per pack with 18 sachets.',
            'image': 'core/products/vetsin.png',
            'price': 35,
            'quantity': 100,
            'reorder_level': 12,
        },
        {
            'name': 'MILO 14*24G',
            'sku': 'MILO-14X24G',
            'category': beverages,
            'description': 'Milo 14 pieces by 24g pack.',
            'image': 'core/products/milo.png',
            'price': 110,
            'quantity': 100,
            'reorder_level': 12,
        },
    ]

    for item in products:
        sku = item.pop('sku')
        Product.objects.update_or_create(sku=sku, defaults=item)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.RunPython(seed_products, migrations.RunPython.noop),
    ]
