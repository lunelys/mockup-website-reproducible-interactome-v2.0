# Author: Lunelys RUNESHAW <lunelys.runeshaw@etudiant.univ-rennes.fr>
#
# personalization of the admin side allowing the user to upload the excel result files from the reproducible-interactome scripts
# populating automatically the SQLite database from the csv files uploaded in admin
# savage pre-processing of these files with the "prepare_table" part
# when switching from test version to real version, you'll have to switch from SQLite to mySQL

from io import StringIO
import pandas as pd
from datetime import datetime
import re
from django.contrib import admin
from .models import Prot
from django.db.models import Q
from django.urls import path
from django.shortcuts import render
from django import forms
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError

admin.site.register(Prot)


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()


class ExpEvAdmin(admin.ModelAdmin):
    print(datetime.now())
    list_display = ('prot1', 'prot2', 'gene1', 'gene2', 'idm', 'pub_id', 'authors', 'species1', 'species2')

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv), ]
        return new_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            now = datetime.now().strftime('%Y-%m-%d')
            csv_file = request.FILES["csv_upload"]
            if not re.search('interactome_all_\d+_tab27_no_redundancies.csv', csv_file.name):
                messages.warning(request,
                                 'The wrong file type was uploaded. Only a file named as "interactome_all_'
                                 '[taxid of 1 species]_tab27_no_redundancies.csv" will be accepted')
                return HttpResponseRedirect(request.path_info)
            csv_file_taxid = csv_file.name.split('_')[2]
            # if rows inside db already have that species taxid, delete
            Prot.objects.filter(csv_file_taxid=csv_file_taxid).delete()

            file_data = csv_file.read().decode("utf-8")
            csvStringIO = StringIO(file_data)

            # savage pre-processing of the excel result files we get from the reproducible-interactome script
            # ============ PREPARE_TABLES.PY =================
            def reorder_psi_mis(row):
                if row != '-':
                    cleaned = []
                    fields = row.split('|')
                    for field in fields:
                        text = field.split('(')[1].replace(')', '')
                        mi = field.split('"')[1].split('"')[0]
                        field = text + ' (' + mi + ')'
                        cleaned.append(field)
                    return "|".join(cleaned)
                else:
                    return row

            def remove_prefix(row):
                if row != '-':
                    cleaned = []
                    fields = row.split('|')
                    for field in fields:
                        field = field.split(':')[1]
                        cleaned.append(field)
                    return "|".join(cleaned)
                else:
                    return row

            def preparing(csv):
                df = pd.read_csv(csv)
                df = df.drop('count_expl', axis=1)
                df['idm'] = df['idm'].apply(reorder_psi_mis)
                df['interaction_type'] = df['interaction_type'].apply(reorder_psi_mis)
                df['source_databases'] = df['source_databases'].apply(reorder_psi_mis)
                df['biological_role1'] = df['biological_role1'].apply(reorder_psi_mis)
                df['biological_role2'] = df['biological_role2'].apply(reorder_psi_mis)
                df['exp_role1'] = df['exp_role1'].apply(reorder_psi_mis)
                df['exp_role2'] = df['exp_role2'].apply(reorder_psi_mis)
                df['interactor_type1'] = df['interactor_type1'].apply(reorder_psi_mis)
                df['interactor_type2'] = df['interactor_type2'].apply(reorder_psi_mis)
                df['participant_id_method1'] = df['participant_id_method1'].apply(reorder_psi_mis)
                df['participant_id_method2'] = df['participant_id_method2'].apply(reorder_psi_mis)
                df['pub_id'] = df['pub_id'].apply(remove_prefix)
                df['species1'] = df['species1'].apply(remove_prefix)
                df['species2'] = df['species2'].apply(remove_prefix)
                df['taxid_host'] = df['taxid_host'].apply(remove_prefix)
                df.replace({'\|': '\n'}, regex=True, inplace=True)
                df['csv_file_taxid'] = csv_file_taxid
                df['csv_file_date'] = now
                df['onlyMIs'] = df['idm'].apply(lambda x: re.findall('MI:\d+', x))
                df['onlyMIs_str'] = df['onlyMIs'].apply(lambda x: ''.join(x))
                # IF IN V3.0 MORE COLUMNS ARE USED (exp_role etc), CHANGE THE LINE BELOW TO UPDATE THE ID ACCORDINGLY
                # + ideally use integer ids
                df['id'] = df['prot1'] + df['prot2'] + df['onlyMIs_str'] + df['pub_id']
                df = df.drop('onlyMIs_str', axis=1)
                df = df.set_index('id')
                df = df.reset_index(names='id')
                return df

            # ============  END PREPARE_TABLES.PY =================

            df_data = preparing(csvStringIO)
            for index, row in df_data.iterrows():
                if set(row[31]).issubset(set(['MI:0676', 'MI:0004'])):
                    print(row[0], row[31])  # icontained_by icontains
                # handle duplicates as good as we can, to improve in a V3.0:
                qs = Prot.objects.filter(Q(prot1__iexact=row[1]) & Q(prot2__iexact=row[2]) & Q(pub_id__iexact=row[7]))
                flag = True
                for ProtObject in qs:
                    if set(row[5].split('\n')).issuperset(set(ProtObject.idm.split('\n'))):
                        ProtObject.delete()
                for mi_row in set(row[5].split('\n')):
                    if qs.filter(idm__contains=mi_row):  # checks if field in ProtObj contains all values within a list
                        flag = False
                if flag:

                    # when switching to test version to real version, you'll have to switch from SQLite to mySQL.
                    # https://docs.djangoproject.com/en/4.2/topics/db/queries/#containment-and-key-lookups SHOULD WORK WITH MYSQL
                    # print(row[31])
                    # qs_subset = Prot.objects.filter(Q(prot1__iexact=row[1]) & Q(prot2__iexact=row[2]) & Q(pub_id__iexact=row[7]) & Q(onlyMIs__contained_by=row[31]))
                    # if qs_subset.exists():
                    #     print(qs_subset.values('id')[0]['id'])
                    # qs_subset.delete()
                    # qs_superset = Prot.objects.filter(Q(prot1__iexact=row[1]) & Q(prot2__iexact=row[2]) & Q(pub_id__iexact=row[7]) & Q(onlyMIs__contains=row[31]))
                    # print(qs_superset)
                    # if qs_superset.exists():
                    #     print(qs_superset.values('id')[0]['id'])
                    # if not qs_superset:  # if there is no superset of the current row, we can create it
                    #     print("=====")
                    #     print(row[0])

                    try:
                        created = Prot.objects.update_or_create(
                            id=row[0],
                            prot1=row[1],
                            prot2=row[2],
                            gene1=row[3],
                            gene2=row[4],
                            idm=row[5],
                            authors=row[6],
                            pub_id=row[7],
                            species1=row[8],
                            species2=row[9],
                            interaction_type=row[10],
                            source_databases=row[11],
                            interaction_identifiers=row[12],
                            confidence_score=row[13],
                            biological_role1=row[14],
                            biological_role2=row[15],
                            exp_role1=row[16],
                            exp_role2=row[17],
                            interactor_type1=row[18],
                            interactor_type2=row[19],
                            taxid_host=row[20],
                            participant_id_method1=row[21],
                            participant_id_method2=row[22],
                            service_name=row[23],
                            biogrid_experimental_system=row[24],
                            biogrid_description=row[25],
                            biogrid_type=row[26],
                            throughput=row[27],
                            count_impl=row[28],
                            csv_file_taxid=row[29],
                            csv_file_date=row[30],
                            onlyMIs=row[31],
                        )
                    except IntegrityError:
                        pass
            url = reverse('admin:index')
            return HttpResponseRedirect(url)

        form = CsvImportForm()
        data = {"form": form}
        print(datetime.now())
        return render(request, "admin/csv_upload.html", data)


admin.site.unregister(Prot)  # to see
admin.site.register(Prot, ExpEvAdmin)
