# Generated by Django 4.2.2 on 2023-07-09 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Prot',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('prot1', models.CharField(default='-', max_length=25, verbose_name='prot1')),
                ('prot2', models.CharField(default='-', max_length=25, verbose_name='prot2')),
                ('gene1', models.CharField(default='-', max_length=40, verbose_name='gene1')),
                ('gene2', models.CharField(default='-', max_length=40, verbose_name='gene2')),
                ('idm', models.CharField(default='-', max_length=255, verbose_name='idm')),
                ('authors', models.CharField(default='-', max_length=255, verbose_name='authors')),
                ('pub_id', models.CharField(default='-', max_length=25, verbose_name='pub_id')),
                ('species1', models.CharField(default='-', max_length=40, verbose_name='species1')),
                ('species2', models.CharField(default='-', max_length=40, verbose_name='species2')),
                ('interaction_type', models.CharField(default='-', max_length=255, verbose_name='interaction_type')),
                ('source_databases', models.CharField(default='-', max_length=150, verbose_name='source_databases')),
                ('interaction_identifiers', models.CharField(default='-', max_length=150, verbose_name='interaction_identifiers')),
                ('confidence_score', models.CharField(default='-', max_length=150, verbose_name='confidence_score')),
                ('biological_role1', models.CharField(default='-', max_length=255, verbose_name='biological_role1')),
                ('biological_role2', models.CharField(default='-', max_length=255, verbose_name='biological_role2')),
                ('exp_role1', models.CharField(default='-', max_length=255, verbose_name='exp_role1')),
                ('exp_role2', models.CharField(default='-', max_length=255, verbose_name='exp_role2')),
                ('interactor_type1', models.CharField(default='-', max_length=255, verbose_name='interactor_type1')),
                ('interactor_type2', models.CharField(default='-', max_length=255, verbose_name='interactor_type2')),
                ('taxid_host', models.CharField(default='-', max_length=100, verbose_name='taxid_host')),
                ('participant_id_method1', models.CharField(default='-', max_length=255, verbose_name='participant_id_method1')),
                ('participant_id_method2', models.CharField(default='-', max_length=255, verbose_name='participant_id_method2')),
                ('service_name', models.CharField(default='-', max_length=100, verbose_name='service_name')),
                ('biogrid_experimental_system', models.CharField(default='-', max_length=100, verbose_name='biogrid_experimental_system')),
                ('biogrid_description', models.CharField(default='-', max_length=400, verbose_name='biogrid_description')),
                ('biogrid_type', models.CharField(default='-', max_length=50, verbose_name='biogrid_type')),
                ('throughput', models.CharField(default='-', max_length=100, verbose_name='throughput')),
                ('count_impl', models.PositiveSmallIntegerField(default='0', verbose_name='count_impl')),
                ('csv_file_taxid', models.PositiveIntegerField(default='0', verbose_name='csv_file_taxid')),
                ('csv_file_date', models.DateField(default='2023-07-09', verbose_name='csv_file_date')),
                ('onlyMIs', models.JSONField(default=list, verbose_name='onlyMIs')),
            ],
        ),
    ]
