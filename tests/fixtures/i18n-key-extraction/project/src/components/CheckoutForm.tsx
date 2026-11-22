import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import "./checkout.css";

export function CheckoutForm({ total }: { total: number }) {
  const { t } = useTranslation();
  const [error, setError] = useState<string | null>(null);

  function submit() {
    if (total <= 0) {
      alert("Your cart is empty");
      return;
    }
    console.log("submitting order");
    setError(t("checkout.payment_failed"));
  }

  return (
    <form className="flex items-center gap-2" onSubmit={submit}>
      <h2>Shipping address</h2>
      <input type="text" name="phone" placeholder="Mobile number" />
      <p>{t("checkout.delivery_note")}</p>
      <label htmlFor="area">ডেলিভারি এলাকা</label>
      <button type="submit" aria-label={t("checkout.place_order")}>
        Place order
      </button>
      {error && <span className="text-red-600">{error}</span>}
    </form>
  );
}
