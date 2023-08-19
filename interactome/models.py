from django.db import models
from django.utils.translation import gettext as _
from datetime import datetime


class Prot(models.Model):
    id = models.CharField(max_length=255, primary_key=True, unique=True)
    prot1 = models.CharField(_("prot1"), max_length=25, default='-')
    prot2 = models.CharField(_("prot2"), max_length=25, default='-')
    gene1 = models.CharField(_("gene1"), max_length=40, default='-')
    gene2 = models.CharField(_("gene2"), max_length=40, default='-')
    idm = models.CharField(_("idm"), max_length=255, default='-')
    authors = models.CharField(_("authors"), max_length=255, default='-')
    pub_id = models.CharField(_("pub_id"), max_length=25, default='-')
    species1 = models.CharField(_("species1"), max_length=40, default='-')
    species2 = models.CharField(_("species2"), max_length=40, default='-')
    interaction_type = models.CharField(_("interaction_type"), max_length=255, default='-')
    source_databases = models.CharField(_("source_databases"), max_length=150, default='-')
    interaction_identifiers = models.CharField(_("interaction_identifiers"), max_length=150, default='-')
    confidence_score = models.CharField(_("confidence_score"), max_length=150, default='-')
    biological_role1 = models.CharField(_("biological_role1"), max_length=255, default='-')
    biological_role2 = models.CharField(_("biological_role2"), max_length=255, default='-')
    exp_role1 = models.CharField(_("exp_role1"), max_length=255, default='-')
    exp_role2 = models.CharField(_("exp_role2"), max_length=255, default='-')
    interactor_type1 = models.CharField(_("interactor_type1"), max_length=255, default='-')
    interactor_type2 = models.CharField(_("interactor_type2"), max_length=255, default='-')
    taxid_host = models.CharField(_("taxid_host"), max_length=100, default='-')
    participant_id_method1 = models.CharField(_("participant_id_method1"), max_length=255, default='-')
    participant_id_method2 = models.CharField(_("participant_id_method2"), max_length=255, default='-')
    service_name = models.CharField(_("service_name"), max_length=100, default='-')
    biogrid_experimental_system = models.CharField(_("biogrid_experimental_system"), max_length=100, default='-')
    biogrid_description = models.CharField(_("biogrid_description"), max_length=400, default='-')
    biogrid_type = models.CharField(_("biogrid_type"), max_length=50, default='-')
    throughput = models.CharField(_("throughput"), max_length=100, default='-')
    count_impl = models.PositiveSmallIntegerField("count_impl", default='0')
    csv_file_taxid = models.PositiveIntegerField("csv_file_taxid", default='0')
    csv_file_date = models.DateField("csv_file_date", default=datetime.now().strftime('%Y-%m-%d'))
    onlyMIs = models.JSONField("onlyMIs", default=list)

    # class Meta:
    #     unique_together = ('prot1', 'prot2', 'pubid')
    # from functools import reduce
    # import operator
    # from django.db.models import Q
    #
    # Prot.objects.filter(reduce(operator.and_, (Q(first_name__contains=x) for x in ['x', 'y', 'z'])))
