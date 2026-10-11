from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import action, display

from .models import ExchangeRate
from .services import RatesFetchError, update_rates


@admin.register(ExchangeRate)
class ExchangeRateAdmin(ModelAdmin):
    list_display = ("currency", "rate", "manual_rate", "markup_percent", "effective", "rate_date")
    list_editable = ("manual_rate", "markup_percent")
    readonly_fields = ("currency", "rate", "rate_date", "updated_at")
    fields = ("currency", "rate", "rate_date", "manual_rate", "markup_percent", "updated_at")
    actions_list = ("refresh_rates",)

    def has_add_permission(self, request: HttpRequest) -> bool:
        # Валюты создаются при загрузке курсов, вручную добавлять не нужно
        return False

    @display(description=_("effective rate"))
    def effective(self, obj: ExchangeRate) -> str:
        return f"{obj.effective_rate:,.2f}"

    @action(description=_("Update from Central Bank"), icon="sync")
    def refresh_rates(self, request: HttpRequest) -> HttpResponseRedirect:
        try:
            updated = update_rates()
            self.message_user(
                request, _("Rates updated: %s") % ", ".join(updated), messages.SUCCESS
            )
        except RatesFetchError as exc:
            self.message_user(request, _("Could not load rates: %s") % exc, messages.ERROR)
        return HttpResponseRedirect(reverse("admin:currency_exchangerate_changelist"))
