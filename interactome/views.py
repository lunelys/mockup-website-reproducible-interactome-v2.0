# Author: Lunelys RUNESHAW <lunelys.runeshaw@etudiant.univ-rennes.fr>
#
# archive view: put in folder /media the files you want to appear in the archive page
# when switching from test version to real version, you'll have to switch from SQLite to mySQL
# TODO: change DB to mySQL -> https://docs.djangoproject.com/en/4.2/intro/tutorial02/

import os
import pandas as pd
import json
from datetime import datetime
from django.http import HttpResponse, FileResponse
from django.shortcuts import render
from django.conf import settings
from django.db.models import Q
from .models import Prot


# This is the index/home page, displaying mainly the search bar
def index(request):
    taxids_in_db = Prot.objects.all().values('csv_file_taxid').distinct()
    in_db = []
    for index, taxid_in_db in enumerate(taxids_in_db):
        taxid_date = Prot.objects.filter(Q(csv_file_taxid=taxid_in_db['csv_file_taxid'])).values('csv_file_date')[0][
            'csv_file_date']
        in_db_dict = {'taxid_in_db': taxid_in_db['csv_file_taxid'],
                      'date_in_db': taxid_date}
        in_db.append(in_db_dict)
    return render(request, 'interactome/index.html', {'in_db': in_db, })


# This is the page that appears when a user search for an interaction, displaying the data as tables from the database
def search(request):
    if request.GET:
        query = request.GET.get('search')
        results = Prot.objects.filter(
            Q(prot1__iexact=query) | Q(prot2__iexact=query) | Q(gene1__iexact=query) | Q(gene2__iexact=query))
        if results.exists():
            df = pd.DataFrame(list(results.values()))
            df = df.drop('onlyMIs', axis=1)
            df[['prot1', 'prot2']] = df[['prot2', 'prot1']] \
                .where(((df['prot2'].str.upper() == query.upper()) | (df['gene2'].str.upper() == query.upper())),
                       df[['prot1', 'prot2']].values)
            df[['gene1', 'gene2']] = df[['gene2', 'gene1']] \
                .where(((df['prot2'].str.upper() == query.upper()) | (df['gene2'].str.upper() == query.upper())),
                       df[['gene1', 'gene2']].values)
            df[['species1', 'species2']] = df[['species2', 'species1']] \
                .where(((df['prot2'].str.upper() == query.upper()) | (df['gene2'].str.upper() == query.upper())),
                       df[['species1', 'species2']].values)
            df[['biological_role1', 'biological_role2']] = df[['biological_role2', 'biological_role1']] \
                .where(((df['prot2'].str.upper() == query.upper()) | (df['gene2'].str.upper() == query.upper())),
                       df[['biological_role1', 'biological_role2']].values)
            df[['exp_role1', 'exp_role2']] = df[['exp_role2', 'exp_role1']] \
                .where(((df['prot2'].str.upper() == query.upper()) | (df['gene2'].str.upper() == query.upper())),
                       df[['exp_role1', 'exp_role2']].values)
            df[['interactor_type1', 'interactor_type2']] = df[['interactor_type2', 'interactor_type1']] \
                .where(((df['prot2'].str.upper() == query.upper()) | (df['gene2'].str.upper() == query.upper())),
                       df[['interactor_type1', 'interactor_type2']].values)
            df[['participant_id_method1', 'participant_id_method2']] = df[
                ['participant_id_method2', 'participant_id_method1']] \
                .where(((df['prot2'].str.upper() == query.upper()) | (df['gene2'].str.upper() == query.upper())),
                       df[['participant_id_method1', 'participant_id_method2']].values)
            df['Count'] = df.groupby(['prot2'])['id'].transform('count')
            df = df.drop_duplicates()
            df = df.sort_values(by=['Count']).reset_index(drop=True)

            checked = ""
            if request.method == "POST":
                if request.POST.get('reproducible') == "True":
                    df = df[df.Count >= 2]
                    checked = "checked"

            result = df.to_json(orient="index")
            parsed = json.loads(result)

            if request.GET.get('format') == 'csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename=interactors_' + query + '.csv'
                if request.GET.get('checked') == "checked":
                    df = df[df.Count >= 2]
                df = df.drop(columns=['id', 'Count', 'onlyMIs'])
                df.to_csv(response, encoding='utf-8', index=False, )
                return response

            return render(request, 'interactome/search.html',
                          {'data': parsed.values(), 'query': query, 'checked': checked, })

        else:
            error_message = 'No results for "' + query + '". Try another protein or check for any spelling error.'
            return render(request, 'interactome/index.html', {'error_message': error_message, })


# This is the page that appears when a user click on "archive" in the navbar, displaying previous files to download
def archive(request):
    now = datetime.now().strftime('%Y-%m-%d')
    current_filename = 'reproducible_interactome_all_latest_' + now + '.csv'
    files = []
    for item in os.scandir(settings.MEDIA_ROOT):
        temp_dict = {
            'name': item.name,
            'modified': datetime.fromtimestamp(item.stat().st_mtime).strftime('%d-%m-%Y'),
            'size': f"{item.stat().st_size / (1 << 17):,.0f}MB"
        }
        files.append(temp_dict)

    if request.GET.get('format') == 'csv':
        path_file = os.path.join(settings.MEDIA_ROOT, request.GET.get('search'))
        file = open(path_file, 'rb')
        response = FileResponse(file, as_attachment=True)
        return response
    elif request.GET.get('current') == 'current':
        results = Prot.objects.all()
        df = pd.DataFrame(list(results.values()))
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + current_filename
        df = df.drop(columns=['id'])
        df.to_csv(response, encoding='utf-8', index=False, )
        return response
    return render(request, 'interactome/archive.html', {'total_files': files,
                                                        'path': settings.MEDIA_ROOT,
                                                        'filename': current_filename, })


# This is the page that appears when a user click on "about" in the navbar, displaying basic info about the project
def about(request):
    return render(request, 'interactome/about.html')


# not used for the moment: maybe to add later, for a better tooltip function
definitions = {
    "Affinity Capture-Luminescence": "An interaction is inferred when a bait protein, tagged with luciferase, is enzymatically detected in immunoprecipitates of the prey protein as light emission. The prey protein is affinity captured from cell extracts by either polyclonal antibody or epitope tag.",
    "Affinity Capture-MS": "The bait protein is affinity captured from cell extracts by either polyclonal antibody or epitope tag and the associated interaction partner is identified by MS methods.",
    "Affinity Capture-RNA": "An interaction is inferred when a 'bait' protein is affinity captured from cell extracts by either polyclonal antibody or epitope tag and the associated interaction partner is an RNA molecule.",
    "Affinity Capture-Western": "The bait protein is affinity captured from cell extracts by either polyclonal antibody or epitope tag and the associated interaction partner is identified by western blot with a specific polyclonal antibody or a second epitope tag. This category is also used if an interacting protein was visualized directly by dye stain or radioactivity.",
    "Biochemical Activity": "Interaction is inferred from a biochemical effect of one protein upon another, for example, GTP-GDP exchange activity or phosphorylation of a substrate by a kinase.",
    "Co-crystal Structure": "Interaction is directly demonstrated at the atomic level by X-ray crystallography.",
    "Co-fractionation": "Interaction is inferred from the presence of two or more protein subunits in a partially purified protein preparation.",
    "Co-localization": "Interaction is inferred from two proteins that co-localize in the cell by indirect immunofluorescence, usually in a co-dependent manner. This category also includes co-dependent association of proteins with promoter DNA in chromatin immunoprecipitation experiments.",
    "Co-purification": "Interaction is inferred from the identification of two or more protein subunits in a purified protein complex, as obtained by classical biochemical fractionation or by affinity purification and one or more additional fractionation steps.",
    "Far Western": "Interaction is detected between a protein immobilized on a membrane and a purified protein probe.",
    "FRET": "The close proximity of interaction partners is detected by fluorescence resonance energy transfer (FRET) between cyan fusion protein (CFP) and yellow fluorescent protein (YFP) fusion proteins in vivo.",
    "PCA": "A protein-protein interaction assay in which a bait protein is expressed as fusion to one of the either N- or C- terminal peptide fragments of a reporter protein and prey protein is expressed as fusion to the complementary N- or C- terminal fragment of the same reporter protein. Interaction of bait and prey proteins bring together complementary fragments, which can then fold into an active reporter.",
    "Protein-peptide": "Interaction is detected between a protein and a peptide derived from an interaction partner. This category includes phage-display experiments.",
    "Protein-RNA": "Interaction is detected between a purified protein and associated RNA(s) as detected by northern blot or reverse transcription-PCR. Genome-wide experiments based on microarray detection were classified as HTP, and not recorded, unless supporting documentation for specific interactions was provided.",
    "Reconstituted Complex": "Interaction is directly detected between purified proteins in vitro, usually in recombinant form.",
    "Two-hybrid": "The bait protein is expressed as a DNA-binding domain fusion and the prey protein is expressed as a transcriptional activation domain fusion and interaction is measured by reporter gene activation. This category was also used for two-hybrid variations such as the split-ubiquitin assay.",
    "Dosage Growth Defect": "The overexpression or increased dosage of one gene causes a growth defect in a strain that is mutated or deleted for another gene.",
    "Dosage Lethality": "The overexpression or increased dosage of one gene causes lethality in a strain that is mutated or deleted for another gene.",
    "Dosage Rescue": "The overexpression or increased dosage of one gene rescues the lethality or growth defect of a strain that is mutated or deleted for another gene.",
    "Synthetic Growth Defect": "Mutations or deletions in separate genes, each of which alone causes a minimal phenotype but when combined in the same cell results in a significant growth defect under a given condition.",
    "Synthetic Haploinsufficiency": "A genetic interaction is inferred when mutations or deletions in separate genes, at least one of which is hemizygous, cause a minimal phenotype alone but result in lethality when combined in the same cell under a given condition.",
    "Synthetic Lethality": "Mutations or deletions in separate genes, each of which alone causes a minimal phenotype but when combined in the same cell results in lethality under a given condition.",
    "Synthetic Rescue": "A mutation or deletion of one gene rescues the lethality or growth defect of a strain mutated or deleted for another gene.",
    "Phenotypic Enhancement": "The mutation, deletion, or overexpression of one gene results in enhancement of any phenotype associated with the mutation, deletion, or over-expression of another gene.",
    "Phenotypic Suppression": "The mutation, deletion, or overexpression of one gene results in the suppression of any phenotype associated with the mutation, deletion, or over-expression of another gene.",
    "Proximity Label-MS": "An interaction is inferred when a bait-enzyme fusion protein selectively modifies a vicinal protein with a diffusible reactive product, followed by affinity capture of the modified protein and identification by mass spectrometric methods.",
    "Positive Genetic": "Mutations/deletions in separate genes, each of which alone causes a minimal phenotype, but when combined in the same cell results in a more severe fitness defect or lethality under a given condition. This term is reserved for high or low throughput studies with scores.",
    "Negative Genetic": "Mutations/deletions in separate genes, each of which alone causes a minimal phenotype, but when combined in the same cell results in a less severe fitness defect than expected under a given condition. This term is reserved for high or low throughput studies with scores."}
