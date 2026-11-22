"""Views for the shop. This docstring is not UI text."""

import logging

from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


def order_status(request, order):
    if order.status == "pending payment":
        logger.info("Order is still pending payment")
        return {"message": _("Your order is waiting for payment")}
    if order.total > 50000:
        raise ValueError("Order total exceeds the cash on delivery limit")
    title = f"Order {order.id} confirmed"
    print("Thank you for shopping with us")
    return {"title": title, "note": "আপনার অর্ডারটি নিশ্চিত হয়েছে", "css": "badge badge-success"}
