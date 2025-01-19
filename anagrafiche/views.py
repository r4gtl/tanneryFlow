import datetime

# from articoli.models import ListinoCliente, ListinoTerzista, PrezzoListino
from django.apps import apps
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.utils import IntegrityError
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django_filters.views import FilterView


from .filters import ClienteFilter, FornitoreFilter, TransferValueFilter
from .forms import (
    FormCliente,
    FormFacility,
    FormFacilityContact,
    FormFornitore,
    FormLwgFornitore,
    FormTransferValue,
    FormXrTransferValueLwgFornitore,
    DestinazioneDiversaFornitoreModelForm,
)
from .models import (
    Cliente,
    Facility,
    FacilityContact,
    Fornitore,
    LwgFornitore,
    TransferValue,
    XrTransferValueLwgFornitore,
    DestinazioneDiversaFornitore,
)

# Create your views here.


def home_fornitori(request):
    fornitori = Fornitore.objects.all()
    fornitori_filter = FornitoreFilter(request.GET, queryset=fornitori)
    # filterset_class = FornitoreFilter
    page = request.GET.get("page", 1)
    paginator = Paginator(
        fornitori_filter.qs, 50
    )  # Utilizza fornitori_filter.qs per la paginazione

    try:
        fornitori_paginator = paginator.page(page)
    except PageNotAnInteger:
        fornitori_paginator = paginator.page(1)
    except EmptyPage:
        fornitori_paginator = paginator.page(paginator.num_pages)

    context = {
        #'fornitori': filterset_class,
        "fornitori_paginator": fornitori_paginator,
        "filter": fornitori_filter,
        "CHOICES_CATEGORY": Fornitore.CHOICES_CATEGORY,
    }
    return render(request, "anagrafiche/home_fornitori.html", context)


class UpdateSupplier(LoginRequiredMixin, UpdateView):
    model = Fornitore
    template_name = "anagrafiche/fornitore.html"
    form_class = FormFornitore

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()  # Utilizza il form principale per Fornitore
        context["pk_fornitore"] = self.object.pk
        # Ottieni l'istanza di Categoria correlata al Fornitore attuale
        categoria_model_name = (
            f'Fornitore{self.object.categoria.title().replace(" ", "")}'
        )

        if categoria_model_name != "FornitoreNessuna":
            categoria_model = apps.get_model(
                app_label="anagrafiche", model_name=categoria_model_name
            )

            if categoria_model:
                print("categoria_model:" + str(categoria_model))
                categoria_instance = categoria_model.objects.filter(
                    fornitore_ptr=self.object
                ).first()
                if categoria_instance:
                    CategoriaForm = modelform_factory(
                        categoria_model, exclude=["fornitore"]
                    )
                    nome_form_secondario = CategoriaForm.__name__
                    context["nome_form_secondario"] = nome_form_secondario
                    modello_form = CategoriaForm(instance=categoria_instance)
                    context["modello_form"] = modello_form
                else:
                    context["categoria_instance_missing"] = (
                        True  # Aggiungi questa chiave al contesto
                    )

        context["lwg_certs"] = LwgFornitore.objects.filter(
            fk_fornitore_id=self.object.pk
        )
        context["destinazioni_diverse"] = DestinazioneDiversaFornitore.objects.filter(
            fk_fornitore=self.object.pk
        )
        print(f"fk_fornitore: {self.object.pk}")
        return context

    def get_success_url(self):
        if "salva_esci" in self.request.POST:
            return reverse_lazy("anagrafiche:home_fornitori")

        pk_fornitore = self.object.pk
        return reverse_lazy("anagrafiche:vedi_fornitore", kwargs={"pk": pk_fornitore})

    def form_valid(self, form):
        messages.info(
            self.request, "Il fornitore è stato modificato!"
        )  # Compare sul success_url
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            categoria_model_name = (
                f'Fornitore{self.object.categoria.title().replace(" ", "")}'
            )
            if categoria_model_name != "FornitoreNessuna":
                categoria_model = apps.get_model(
                    app_label="anagrafiche", model_name=categoria_model_name
                )
                if categoria_model:
                    categoria_instance = categoria_model.objects.filter(
                        fornitore_ptr=self.object
                    ).first()

                    if not categoria_instance:
                        categoria_instance = categoria_model.objects.create(
                            fornitore_ptr=self.object
                        )

                    CategoriaForm = modelform_factory(
                        categoria_model, exclude=["fornitore"]
                    )
                    categoria_form = CategoriaForm(
                        request.POST, instance=categoria_instance
                    )
                    if categoria_form.is_valid():
                        categoria_form.save()

            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        # messages.error(self.request, 'Errore! Il fornitore non è stato aggiunto!')
        return super().form_invalid(form)


def aggiungi_fornitore_with_category(request, category):
    context = {
        "category": category,
        "CHOICES_CATEGORY": Fornitore.CHOICES_CATEGORY,
    }
    return render(request, "anagrafiche/aggiungi_fornitore_modal.html", context)


class CreateSupplier(LoginRequiredMixin, CreateView):

    model = Fornitore
    form_class = FormFornitore
    success_message = "Fornitore aggiunto correttamente!"
    error_message = "Error saving the Doc, check fields below."
    template_name = "anagrafiche/fornitore.html"

    def get_initial(self):
        initial = super().get_initial()
        created_by = self.request.user
        categoria = self.request.GET.get("categoria")
        if categoria in dict(Fornitore.CHOICES_CATEGORY):
            initial["categoria"] = categoria
            print("categoria initial: " + str(categoria))
        initial["created_by"] = created_by
        initial["created_at"] = datetime.datetime.now()
        return initial

    def get_success_url(self):
        if "salva_esci" in self.request.POST:
            return reverse_lazy("anagrafiche:home_fornitori")

        pk_fornitore = self.object.pk
        print("pk_fornitore: " + str(pk_fornitore))
        return reverse_lazy("anagrafiche:vedi_fornitore", kwargs={"pk": pk_fornitore})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CHOICES_CATEGORY"] = Fornitore.CHOICES_CATEGORY
        return context

    def form_valid(self, form):
        forn = form.save(commit=False)
        forn.created_by = self.request.user
        forn.created_at = datetime.datetime.now()
        categoria = form.cleaned_data["categoria"]
        forn.save()

        print("categoria: " + str(categoria))

        if categoria == Fornitore.NESSUNA:  # Nessuna categoria selezionata
            forn.save()
            messages.info(self.request, "Il fornitore è stato aggiunto!")
            self.object = forn
            return HttpResponseRedirect(self.get_success_url())

        categoria_model_name = f'Fornitore{categoria.title().replace(" ", "")}'
        print("categoria_model_name: " + str(categoria_model_name))
        categoria_model = apps.get_model(
            app_label="anagrafiche", model_name=categoria_model_name
        )

        if categoria_model:
            try:
                # Crea l'istanza del modello specifico per la categoria senza salvarla
                categoria_instance = categoria_model(fornitore_ptr=forn)

                # Aggiungi qui la mappatura tra categoria e attributo forn.fornitore_ptr_* corretto
                categoria_attr_map = {
                    "FornitorePelli": "fornitore_ptr_pelli",
                    "FornitoreProdottiChimici": "fornitore_ptr_prodottichimici",
                    "FornitoreManutenzioni": "fornitore_ptr_manutenzioni",
                    "FornitoreLavorazioniEsterne": "fornitore_ptr_lavorazioniesterne",
                    "FornitoreServizi": "fornitore_ptr_servizi",
                    "FornitoreRifiuti": "fornitore_ptr_rifiuti",
                    # Aggiungi altri se necessario
                }

                categoria_attr = categoria_attr_map.get(categoria_model_name)
                print("categoria_attr: " + str(categoria_attr))
                if categoria_attr:
                    setattr(forn, categoria_attr, categoria_instance)
                    categoria_instance = categoria_model.objects.create(
                        fornitore_ptr=forn
                    )
                    forn.save()  # Salva l'istanza del modello generico con la relazione
            except IntegrityError as e:
                forn.delete()
                messages.error(
                    self.request, "Errore! Il fornitore non è stato aggiunto!"
                )
                return super().form_invalid(form)

        self.object = forn
        messages.info(self.request, "Il fornitore è stato aggiunto!")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Errore! Il fornitore non è stato aggiunto!")
        return super().form_invalid(form)


# Destinazioni diverse fornitori
class DestinazioneDiversaFornitoreCreateView(LoginRequiredMixin, CreateView):
    model = DestinazioneDiversaFornitore
    form_class = DestinazioneDiversaFornitoreModelForm
    template_name = "anagrafiche/destinazione_diversa_fornitore.html"
    success_message = "Destinazione diversa aggiunta correttamente!"

    def get_success_url(self):

        if "salva_esci" in self.request.POST:
            fornitore = self.object.fk_fornitore.pk
            # print("Fornitore: " + str(fornitore))
            return reverse_lazy("anagrafiche:vedi_fornitore", kwargs={"pk": fornitore})

        pk = self.object.pk
        return reverse_lazy(
            "anagrafiche:modifica_destinazione_diversa_fornitore", kwargs={"pk": pk}
        )

    def get_initial(self):
        fk_fornitore = self.kwargs["fk_fornitore"]
        return {
            "fk_fornitore": fk_fornitore,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fk_fornitore = self.kwargs["fk_fornitore"]
        print("Fornitore: " + str(fk_fornitore))
        context["fornitore"] = Fornitore.objects.get(pk=fk_fornitore)
        context["fk_fornitore"] = fk_fornitore
        return context


class DestinazioneDiversaFornitoreUpdateView(LoginRequiredMixin, UpdateView):
    model = DestinazioneDiversaFornitore
    form_class = DestinazioneDiversaFornitoreModelForm
    template_name = "anagrafiche/destinazione_diversa_fornitore.html"
    success_message = "Destinazione diversa modificata correttamente!"

    def get_success_url(self):
        if "salva_esci" in self.request.POST:
            fornitore = self.object.fk_fornitore.pk
            # print("Fornitore: " + str(fornitore))
            return reverse_lazy("anagrafiche:vedi_fornitore", kwargs={"pk": fornitore})

        pk = self.object.pk
        # print(f'pk da success url: {pk}')
        return reverse_lazy(
            "anagrafiche:modifica_destinazione_diversa_fornitore", kwargs={"pk": pk}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fk_fornitore = self.object.fk_fornitore.pk
        context["fk_fornitore"] = fk_fornitore
        context["fornitore"] = Fornitore.objects.get(pk=fk_fornitore)

        return context


def delete_destinazione_diversa_fornitore(request, pk):
    deleteobject = get_object_or_404(DestinazioneDiversaFornitore, pk=pk)
    fornitore = deleteobject.fk_fornitore.pk
    deleteobject.delete()
    messages.warning(request, "Voce eliminata correttamente!")
    url_match = reverse_lazy("anagrafiche:vedi_fornitore", kwargs={"pk": fornitore})
    return redirect(url_match)


class AddLwgCertificate(CreateView):

    model = LwgFornitore
    form_class = FormLwgFornitore
    success_message = "Certificato aggiunto correttamente!"
    error_message = "Error saving the Doc, check fields below."

    template_name = "anagrafiche/lwg.html"

    def get_success_url(self):
        # fornitore=self.object.fk_fornitore.pk

        if "salva_esci" in self.request.POST:
            fornitore = self.object.fk_fornitore.pk
            print("Fornitore: " + str(fornitore))
            return reverse_lazy("anagrafiche:vedi_fornitore", kwargs={"pk": fornitore})

        pk = self.object.pk
        return reverse_lazy("anagrafiche:modifica_lwg", kwargs={"pk": pk})

    def get_initial(self):
        fk_fornitore = self.kwargs["fk_fornitore"]
        return {
            "fk_fornitore": fk_fornitore,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fk_fornitore = self.kwargs["fk_fornitore"]
        print("Fornitore: " + str(fk_fornitore))
        # context['fornitore'] = Fornitore.objects.get(pk=fornitore) # FILTRARE
        context["fornitore"] = Fornitore.objects.get(pk=fk_fornitore)
        context["fk_fornitore"] = fk_fornitore
        return context


class UpdateLwgCertificate(UpdateView):

    model = LwgFornitore
    form_class = FormLwgFornitore
    success_message = "Certificato modificato correttamente!"
    error_message = "Certificato non salvato. Controlla."

    template_name = "anagrafiche/lwg.html"

    def get_success_url(self):
        if "salva_esci" in self.request.POST:
            fornitore = self.object.fk_fornitore.pk
            print("Fornitore: " + str(fornitore))
            return reverse_lazy("anagrafiche:vedi_fornitore", kwargs={"pk": fornitore})

        pk = self.object.pk
        print(f"pk da success url: {pk}")
        return reverse_lazy("anagrafiche:modifica_lwg", kwargs={"pk": pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fk_fornitore = self.object.fk_fornitore.pk
        context["transfer_values"] = XrTransferValueLwgFornitore.objects.filter(
            fk_lwgcertificato=self.object.id
        )
        context["fk_fornitore"] = fk_fornitore
        context["fornitore"] = Fornitore.objects.get(pk=fk_fornitore)

        return context


def delete_certificato(request, pk):
    deleteobject = get_object_or_404(LwgFornitore, pk=pk)
    fornitore = deleteobject.fk_fornitore.pk
    # dettaglio=deleteobject.iddettordine
    # linea = deleteobject.id_linea
    # tempomaster=deleteobject.idtempomaster
    deleteobject.delete()
    url_match = reverse_lazy("anagrafiche:vedi_fornitore", kwargs={"pk": fornitore})
    return redirect(url_match)


class XrTransferValueCreateView(CreateView):
    model = XrTransferValueLwgFornitore
    form_class = FormXrTransferValueLwgFornitore
    success_message = "Transfer Value modificata correttamente!"
    # success_url = reverse_lazy('anagrafiche:modifica_lwg')
    template_name = "anagrafiche/lwg_transfer_values.html"

    def form_valid(self, form):
        messages.info(self.request, self.success_message)  # Compare sul success_url
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fk_certificato = self.kwargs["fk_certificato"]
        print(f"fk_certificato: {fk_certificato}")
        certificato = LwgFornitore.objects.get(pk=fk_certificato)
        fornitore = Fornitore.objects.get(pk=certificato.fk_fornitore.pk)
        context["fornitore"] = fornitore
        context["certificato"] = certificato

        return context

    def get_initial(self):
        fk_certificato = self.kwargs["fk_certificato"]
        certificato = LwgFornitore.objects.get(pk=fk_certificato)
        created_by = self.request.user
        return {"fk_lwgcertificato": certificato.pk, "created_by": created_by}

    def get_success_url(self):
        fk_certificato = self.object.fk_lwgcertificato.pk
        return reverse_lazy("anagrafiche:modifica_lwg", kwargs={"pk": fk_certificato})


class XrTransferValueUpdateView(LoginRequiredMixin, UpdateView):
    model = XrTransferValueLwgFornitore
    form_class = FormXrTransferValueLwgFornitore
    template_name = "anagrafiche/lwg_transfer_values.html"
    success_message = "Transfer Value modificata correttamente!"
    success_url = reverse_lazy("anagrafiche:modifica_lwg")

    def form_valid(self, form):
        messages.info(self.request, self.success_message)  # Compare sul success_url
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        xrtv = XrTransferValueLwgFornitore.objects.get(pk=self.kwargs["pk"])
        fk_certificato = xrtv.fk_lwgcertificato.pk
        certificato = LwgFornitore.objects.get(pk=fk_certificato)
        fornitore = Fornitore.objects.get(pk=certificato.fk_fornitore.pk)
        context["fornitore"] = fornitore
        context["certificato"] = certificato
        return context

    def get_success_url(self):
        lwgcertificate = self.object.fk_lwgcertificato.pk
        return reverse_lazy("anagrafiche:modifica_lwg", kwargs={"pk": lwgcertificate})


def delete_xrtransfervalue(request, pk):
    deleteobject = get_object_or_404(XrTransferValueLwgFornitore, pk=pk)
    fk_certificato = deleteobject.fk_lwgcertificato.pk
    deleteobject.delete()
    url_match = reverse_lazy("anagrafiche:modifica_lwg", kwargs={"pk": fk_certificato})
    return redirect(url_match)


class ListaFornitoriView(FilterView):

    model = Fornitore
    context_object_name = "initial_fornitori"
    template_name = "anagrafiche/home_fornitori.html"
    filterset_class = FornitoreFilter
    paginate_by = 30
    # ordering = ['-iddettordine']


def aggiungi_facility_details(request, pk):
    facility = get_object_or_404(Facility, pk=pk)
    if request.method == "POST":
        form = FormFacility(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.instance.facility = facility
        else:
            form = FormFacility()
        context = {"facility": facility, "form": form}

        return render(request, "anagrafiche/facility.html", context)


class FacilityCreateView(CreateView):
    template_name = "anagrafiche/facility.html"
    form_class = FormFacility


class FacilityUpdateView(UpdateView):
    model = Facility
    template_name = "anagrafiche/facility.html"
    form_class = FormFacility

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["facility_contacts"] = FacilityContact.objects.filter(
            fk_facility=self.object.pk
        )
        return context


def add_facility_contact(request, pk):
    facility = get_object_or_404(Facility, pk=pk)

    if request.method == "POST":
        form = FormFacilityContact(request.POST)
        fk_facility = facility
        nome_cognome = request.POST.get("name")
        contact_type = request.POST.get("contact_type")
        position = request.POST.get("position")
        facility_contact = FacilityContact.objects.create(
            name=nome_cognome,
            contact_type=contact_type,
            position=position,
            fk_facility=fk_facility,
        )
        messages.info(request, "Il contatto è stato aggiunto!")
        return redirect("anagrafiche:edit_facility_details", pk=pk)
    else:
        form = FormFacilityContact()

    return render(
        request,
        "anagrafiche/facility_contacts.html",
        {"facility": facility, "form": form},
    )


class FacilityContactUpdateView(LoginRequiredMixin, UpdateView):
    model = FacilityContact
    form_class = FormFacilityContact
    template_name = "anagrafiche/facility_contacts.html"
    success_message = "Contatto modificato correttamente!"
    # success_url = reverse_lazy('human_resources:tabelle_generiche_formazione')

    def get_success_url(self):
        fk_facility = self.object.fk_facility.pk
        return reverse_lazy(
            "anagrafiche:edit_facility_details", kwargs={"pk": fk_facility}
        )


def delete_facility_contact(request, pk):
    deleteobject = get_object_or_404(FacilityContact, pk=pk)
    fk_facility = deleteobject.fk_facility.pk
    deleteobject.delete()
    messages.warning(request, "Voce eliminata correttamente!")
    url_match = reverse_lazy(
        "anagrafiche:edit_facility_details", kwargs={"pk": fk_facility}
    )
    return redirect(url_match)


# Creazione, Vista e Update Clienti
class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    form_class = FormCliente
    template_name = "anagrafiche/cliente.html"
    success_message = "Cliente aggiunto correttamente!"
    success_url = reverse_lazy("anagrafiche:home_clienti")

    def get_initial(self):
        created_by = self.request.user
        return {"created_by": created_by, "created_at": datetime.datetime.now()}

    def form_valid(self, form):
        messages.info(self.request, self.success_message)  # Compare sul success_url
        return super().form_valid(form)


class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    form_class = FormCliente
    template_name = "anagrafiche/cliente.html"
    success_message = "Cliente modificato correttamente!"
    success_url = reverse_lazy("anagrafiche:home_clienti")

    def form_valid(self, form):
        messages.info(self.request, self.success_message)  # Compare sul success_url
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fk_cliente = self.kwargs["pk"]
        listini = ListinoCliente.objects.filter(fk_cliente=fk_cliente)
        context["listini"] = listini
        return context


class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = "anagrafiche/home_clienti.html"
    paginate_by = 10


class ListaClienteView(FilterView):

    model = Cliente
    context_object_name = "initial_clienti"
    template_name = "anagrafiche/home_clienti.html"
    filterset_class = ClienteFilter
    paginate_by = 30


"""SEZIONE TABELLE GENERICHE"""


def tabelle_generiche(request):
    transfervalues = TransferValue.objects.all()
    tot_transfervalues = TransferValue.objects.count()

    transfervalues_filter = TransferValueFilter(request.GET, queryset=transfervalues)
    filtered_transfervalues = transfervalues_filter.qs  # Ottieni i record filtrati
    transfervalues_filter_count = (
        filtered_transfervalues.count()
    )  # Conta i record filtrati

    """sostanze_filter = SostanzaFilter(request.GET, queryset=sostanze)
    filtered_sostanze = sostanze_filter.qs  # Ottieni i record filtrati
    sostanze_filter_count = filtered_sostanze.count()  # Conta i record filtrati"""

    # Paginazione Sostanze
    page_transfervalues = request.GET.get("page", 1)
    paginator_transfervalues = Paginator(filtered_transfervalues, 50)

    try:
        transfervalues_paginator = paginator_transfervalues.page(page_transfervalues)
    except PageNotAnInteger:
        transfervalues_paginator = paginator_transfervalues.page(1)
    except EmptyPage:
        transfervalues_paginator = paginator_transfervalues.page(
            paginator_transfervalues.num_pages
        )

    context = {
        # Transfer Values
        "transfervalues": transfervalues,
        "transfervalues_paginator": transfervalues_paginator,
        "tot_transfervalues": tot_transfervalues,
        "filter_transfervalues": transfervalues_filter,
        "transfervalues_filter_count": transfervalues_filter_count,
    }

    return render(request, "anagrafiche/generiche/tabelle_generiche.html", context)


# Creazione, Vista e Update Transfer Values
class TransferValueCreateView(LoginRequiredMixin, CreateView):
    model = TransferValue
    form_class = FormTransferValue
    template_name = "anagrafiche/transfer_value.html"
    success_message = "Transfer Value aggiunta correttamente!"
    success_url = reverse_lazy("anagrafiche:tabelle_generiche")


class TransferValueUpdateView(LoginRequiredMixin, UpdateView):
    model = TransferValue
    form_class = FormTransferValue
    template_name = "anagrafiche/transfer_value.html"
    success_message = "Transfer Value modificata correttamente!"
    success_url = reverse_lazy("anagrafiche:tabelle_generiche")

    def form_valid(self, form):
        messages.info(self.request, self.success_message)  # Compare sul success_url
        return super().form_valid(form)


def delete_transfer_value(request, pk):
    deleteobject = get_object_or_404(TransferValue, pk=pk)
    deleteobject.delete()
    messages.warning(request, "Voce eliminata correttamente!")
    url_match = reverse_lazy("anagrafiche:tabelle_generiche")
    return redirect(url_match)
