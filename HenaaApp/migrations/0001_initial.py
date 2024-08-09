# Generated by Django 3.2.25 on 2024-08-09 20:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=255)),
                ('Description', models.TextField()),
                ('Size', models.CharField(max_length=10)),
                ('Color', models.CharField(max_length=50)),
                ('Price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('StockQuantity', models.IntegerField()),
                ('Category', models.CharField(max_length=100)),
                ('ImageURL', models.URLField(max_length=255)),
                ('Created_at', models.DateTimeField(auto_now_add=True)),
                ('Updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('OrderDate', models.DateTimeField(auto_now_add=True)),
                ('TotalAmount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('PaymentStatus', models.CharField(max_length=45)),
                ('Created_at', models.DateTimeField(auto_now_add=True)),
                ('Updated_at', models.DateTimeField(auto_now=True)),
                ('Processed_by', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=225)),
                ('password', models.CharField(max_length=150)),
                ('confirm_pw', models.CharField(max_length=150)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Rating', models.IntegerField()),
                ('Comment', models.TextField()),
                ('ReviewDate', models.DateTimeField(auto_now_add=True)),
                ('Created_at', models.DateTimeField(auto_now_add=True)),
                ('Updated_at', models.DateTimeField(auto_now=True)),
                ('DressID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HenaaApp.dress')),
                ('UserID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HenaaApp.user')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('PaymentDate', models.DateTimeField()),
                ('PaymentAmount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('PaymentMethod', models.CharField(max_length=45)),
                ('Created_at', models.DateTimeField(auto_now_add=True)),
                ('Updated_at', models.DateTimeField(auto_now=True)),
                ('OrderID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HenaaApp.order')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Quantity', models.IntegerField()),
                ('Price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('Created_at', models.DateTimeField(auto_now_add=True)),
                ('Updated_at', models.DateTimeField(auto_now=True)),
                ('DressID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HenaaApp.dress')),
                ('OrderID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HenaaApp.order')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='UserID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HenaaApp.user'),
        ),
        migrations.AddField(
            model_name='dress',
            name='Created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HenaaApp.user'),
        ),
    ]
