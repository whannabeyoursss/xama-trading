# Generated migration file for new features

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_product_image_seed_products'),
    ]

    operations = [
        # Update User model
        migrations.AddField(
            model_name='user',
            name='two_factor_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='email_notifications_enabled',
            field=models.BooleanField(default=True),
        ),
        
        # Update Product model - change image to ImageField
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='products/'),
        ),
        
        # Add updated_at to Order
        migrations.AddField(
            model_name='order',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        
        # Create BulkPrice model
        migrations.CreateModel(
            name='BulkPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_min', models.PositiveIntegerField()),
                ('discount_percent', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bulk_prices', to='core.product')),
            ],
            options={
                'ordering': ['quantity_min'],
                'unique_together': {('product', 'quantity_min')},
            },
        ),
        
        # Create Review model
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.TextField(blank=True)),
                ('approved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='core.user')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='core.product')),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('product', 'customer')},
            },
        ),
        
        # Create OrderStatusHistory model
        migrations.CreateModel(
            name='OrderStatusHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_status', models.CharField(blank=True, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], max_length=20, null=True)),
                ('new_status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], max_length=20)),
                ('changed_at', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True)),
                ('changed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.user')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_history', to='core.order')),
            ],
            options={
                'ordering': ['-changed_at'],
            },
        ),
        
        # Create AuditLog model
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete')], max_length=20)),
                ('model_name', models.CharField(max_length=50)),
                ('object_id', models.PositiveIntegerField()),
                ('changes', models.JSONField(default=dict)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.user')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        
        # Add indexes to AuditLog
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['model_name', 'object_id'], name='core_auditl_model_n_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['user', 'timestamp'], name='core_auditl_user_id_idx'),
        ),
        
        # Create InventoryAlert model
        migrations.CreateModel(
            name='InventoryAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alert_sent_at', models.DateTimeField(auto_now_add=True)),
                ('quantity_at_alert', models.PositiveIntegerField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='core.product')),
            ],
            options={
                'ordering': ['-alert_sent_at'],
            },
        ),
    ]
