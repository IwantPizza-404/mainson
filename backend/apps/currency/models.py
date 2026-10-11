from decimal import ROUND_HALF_UP, Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class ExchangeRate(models.Model):
    """Курс валюты отображения к базовой валюте (USD): сколько единиц валюты за 1 USD.

    Курс подтягивается из ЦБ Узбекистана автоматически. В админке можно задать
    свой курс вместо официального и наценку на конвертацию.
    """

    currency = models.CharField(_("currency"), max_length=3, unique=True)
    rate = models.DecimalField(
        _("official rate"),
        max_digits=18,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0.000001"))],
        help_text=_("Units of currency per 1 USD, updated automatically."),
    )
    manual_rate = models.DecimalField(
        _("manual rate"),
        max_digits=18,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000001"))],
        help_text=_("If set, used instead of the official rate."),
    )
    markup_percent = models.DecimalField(
        _("markup, %"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
        help_text=_("Added to the rate, e.g. to cover conversion costs."),
    )
    rate_date = models.DateField(_("rate date"), null=True, blank=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("exchange rate")
        verbose_name_plural = _("exchange rates")
        ordering = ["currency"]

    def __str__(self) -> str:
        return f"1 USD = {self.effective_rate} {self.currency}"

    @property
    def effective_rate(self) -> Decimal:
        base = self.manual_rate if self.manual_rate is not None else self.rate
        rate = base * (1 + self.markup_percent / 100)
        return rate.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
