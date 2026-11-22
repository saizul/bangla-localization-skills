import json

from conftest import FIXTURES, load_script, run_script

SKILL = "i18n-key-extraction"
SCRIPT = "find_hardcoded.py"
fh = load_script(SKILL, SCRIPT)
F = FIXTURES / SKILL


def texts(findings):
    return {f["text"] for f in findings}


def scan_project(**kw):
    findings, errors = fh.scan([F / "project"], **kw)
    assert errors == []
    return findings


def test_tsx_findings():
    found = texts(f for f in scan_project() if f["file"].endswith("CheckoutForm.tsx"))
    assert {"Your cart is empty", "Shipping address", "Mobile number", "Place order", "ডেলিভারি এলাকা"} <= found
    assert "submitting order" not in found  # console.log
    assert "flex items-center gap-2" not in found  # className
    assert not any(t.startswith("checkout.") for t in found)  # already inside t()


def test_vue_findings():
    found = texts(f for f in scan_project() if f["file"].endswith("Header.vue"))
    assert found == {"Go to homepage", "Sign out"}


def test_php_findings_and_text_domain():
    php = [f for f in scan_project(text_domain="shopbd") if f["file"].endswith("header.php")]
    found = texts(php)
    assert {"Your cart", "Free delivery inside Dhaka", "সকল পণ্যে ১০% ছাড়"} <= found
    assert "Main menu" not in found and "Home" not in found  # wrapped in __() / esc_html_e()
    assert "This comment should be ignored by the scanner." not in found
    domain = {f["text"]: f["message"] for f in php if f["kind"] == "text-domain"}
    assert "no text domain" in domain["Search products"]
    assert "wrong-domain" in domain["Track your order"]


def test_python_findings():
    py = [f for f in scan_project() if f["file"].endswith("views.py")]
    found = texts(py)
    assert {"Thank you for shopping with us", "আপনার অর্ডারটি নিশ্চিত হয়েছে", "Order {x} confirmed"} <= found
    assert "Order total exceeds the cash on delivery limit" in found
    assert "Your order is waiting for payment" not in found  # _()
    assert "Order is still pending payment" not in found  # logger
    assert "pending payment" not in found  # comparison
    assert "badge badge-success" not in found
    assert not any("docstring" in t for t in found)


def test_include_logs():
    py = [f for f in scan_project(include_logs=True) if f["file"].endswith("views.py")]
    assert "Order is still pending payment" in texts(py)


def test_tests_and_vendor_skipped():
    files = {f["file"] for f in scan_project()}
    assert not any("node_modules" in f or ".test." in f for f in files)
    with_tests = {f["file"] for f in scan_project(include_tests=True)}
    assert any(".test." in f for f in with_tests)


def test_clean_project_has_no_findings():
    findings, _ = fh.scan([F / "clean"])
    assert [f for f in findings if f["confidence"] != "low"] == []


def test_looks_user_facing():
    assert fh.looks_user_facing("Save your changes") == "medium"
    assert fh.looks_user_facing("Save") == "low"
    assert fh.looks_user_facing("সংরক্ষণ করুন") == "high"
    for not_ui in (
        "btn btn-primary",
        "/api/v1/orders",
        "application/json",
        "GET",
        "SELECT * FROM x",
        "user_id",
        "%s: %s",
        "https://example.com",
        "a@example.com",
    ):
        assert fh.looks_user_facing(not_ui) is None, not_ui


def test_keys_are_unique_and_slugged():
    findings = [
        {"key": "a.save", "text": "Save"},
        {"key": "a.save", "text": "Save!"},
        {"key": "a.save", "text": "Save"},
    ]
    catalog = fh.unique_keys(findings)
    assert catalog == {"a.save": "Save", "a.save_2": "Save!"}
    assert (
        fh.suggest_key("Place your ${n} orders now please", "checkout", 3)
        == "checkout.place_your_orders_now_please"
    )
    assert fh.namespace_for(fh.Path("src/components/CheckoutForm.tsx")) == "checkout_form"


def test_cli_and_catalog(tmp_path):
    out = tmp_path / "catalog.json"
    r = run_script(SKILL, SCRIPT, str(F / "project"), "--emit-catalog", str(out), "--json")
    assert r.returncode == 1
    data = json.loads(r.stdout)
    assert data["count"] >= 10
    catalog = json.loads(out.read_text(encoding="utf-8"))
    assert catalog["checkout_form.place_order"] == "Place order"
    again = run_script(SKILL, SCRIPT, str(F / "project"), "--emit-catalog", str(out))
    assert again.returncode == 2 and "exists" in again.stderr
    clean = run_script(SKILL, SCRIPT, str(F / "clean"))
    assert clean.returncode == 0
    high = run_script(SKILL, SCRIPT, str(F / "project"), "--min-confidence", "high", "--json")
    assert all(f["confidence"] == "high" for f in json.loads(high.stdout)["findings"])
    assert run_script(SKILL, SCRIPT, str(tmp_path / "missing")).returncode == 2
    assert run_script(SKILL, SCRIPT, "--help").returncode == 0
