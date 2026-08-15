# بسته تکمیل ST1-136 برای selected series

## هدف این بسته

این بسته برای تکمیل **فقط** ورودی‌های باقی‌مانده‌ی مسیر selected-series در
ST1-066 است؛ همان مسیری که باید در نهایت یک record واقعی را بدون تضعیف trust
controls تا `policy_automatic` برساند و قبل از certification متوقف شود.

این بسته:

- source boundary جدید ایجاد نمی‌کند؛
- activation انجام نمی‌دهد؛
- source registration اجرا نمی‌کند؛
- native acquisition اجرا نمی‌کند؛
- certification انجام نمی‌دهد؛
- current status پروژه را اعلام نمی‌کند.

## series هدف

- `target_source_id`: `maroon_project_controls_progress_workbook_series`
- workbook نماینده شناخته‌شده: `070-TWRP-24 1402-12-05.xlsx`
- نمونه reporting period شناخته‌شده: `1402/11/21–1402/12/05`

## آنچه از قبل دریافت شده است

### A1 — دریافت شده

این مورد قبلاً دریافت شده و در evidence محلی ثبت شده است:

- signer: `صحرا حیدری`
- title: `مدیر سیستم`
- confirmed role: `Pilot Sponsor / Pilot Governance Authority`
- effective date: `2026-08-11`

reference:

- `evidence/sanitized/2026-08-11-st1-135-a1-pilot-governance-attestation.json`

### محدودیت A1

A1 فقط pilot governance محدود SDAS / Data Insurance را پوشش می‌دهد و این‌ها را
ایجاد نمی‌کند:

- historical Project Controls authority
- historical source ownership
- historical document authority
- authority of the Maroon workbook series
- current project status
- certification
- reliance eligibility

## آنچه هنوز باید برگردد

### بسته 1 — A2 / A3 / source-registration / series-id supplement

برای این بخش از این template استفاده شود:

- `docs/examples/ST1_136_selected_series_remaining_inputs.template.json`

و اگر لازم بود، از این سند توضیحی استفاده شود:

- `docs/ST1_136_REMAINING_SELECTED_SERIES_INPUTS_FA.md`

#### چه کسی باید A2 را بدهد؟

کسی که به‌صورت رسمی و قابل‌اتکا می‌تواند مشخص کند کدام role سازمانی مسئول
Project Controls / PMO برای همین recurring workbook/report class در پروژه
Maroon است.

#### چه کسی باید A3 را بدهد؟

کسی که به‌صورت رسمی و قابل‌اتکا می‌تواند تعریف controlled report/workbook
class را برای همین series مشخص کند، مخصوصاً:

- محل رسمی reporting period
- convention نسخه / revision / document number
- rule issue / approval / release

#### چه چیزی باید همراه supplement برگردد؟

- A2
- A3
- `stable_source_registration_evidence_reference`
- `stable_non_sensitive_source_series_identifier`

### بسته 2 — selected-series native-record artifact

برای این بخش از این template استفاده شود:

- `docs/examples/ST1_136_selected_series_native_record.template.json`

این artifact باید برای **همین** selected series باشد، نه یک source دیگر.

حداقل باید این‌ها را داشته باشد:

- `source_id = maroon_project_controls_progress_workbook_series`
- source type
- non-sensitive location class
- acquisition metadata
- original fingerprint
- deterministic transformation lineage
- resolved reporting/business time
- policy context

## rule مهم business time

business/reporting time فقط از این‌ها معتبر است:

- header دارای reporting week / reporting period
- field رسمی و مشخص reporting period

این‌ها معتبر نیستند:

- filesystem timestamp
- acquisition timestamp
- row-level planned date
- row-level target date

## مسئول تحویل نهایی چه چیزی باید برگرداند؟

فقط این دو artifact sanitize‌شده:

1. supplement تکمیل‌شده برای A2/A3/source-registration/series-id
2. native-record artifact تکمیل‌شده برای همین selected series

## وقتی این دو artifact رسیدند، چه commandی باید اجرا شود؟

اگر قرار باشد کل مسیر post-A1 در یک فرمان سنجیده شود، این command استفاده شود:

```powershell
python scripts/run_st1_136_post_a1_submission_gate.py `
  --base-bundle evidence/sanitized/2026-08-11-st1-135-selected-series-bundle.partial.a1.json `
  --supplement <real-st1-136-supplement.json> `
  --native-record <real-selected-series-native-record.json>
```

## خروجی truthful مورد انتظار

اگر هر دو artifact:

- exact-scope باشند،
- structurally acceptable باشند،
- و با selected series match باشند،

آنگاه next truthful step فقط این است:

`begin_independent_controlled_review`

نه بیشتر.

## متن کوتاه قابل‌ارسال

> A1 برای pilot governance محدود دریافت شده است. برای ادامه مسیر واقعی ST1-066
> روی `maroon_project_controls_progress_workbook_series` فقط دو artifact
> sanitize‌شده‌ی دیگر لازم است:
>
> 1. supplement تکمیل‌شده‌ی A2/A3/source-registration/series-id
> 2. native-record artifact تکمیل‌شده برای همین selected series
>
> لطفاً فقط همین دو artifact را برگردانید. این درخواست به معنی activation،
> certification یا current-status declaration نیست.
