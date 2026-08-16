# ST1-139 — پیشنهاد واحد تصمیم Governance برای مسیر prospective selected series

## هدف

این پیشنهاد فقط برای governance prospective در pilot SDAS/Data Insurance است و فقط به این selected series محدود می‌شود:

- `maroon_project_controls_progress_workbook_series`

این پیشنهاد درباره اسناد/گزارش‌های آینده‌ی همین series است و برای evidenceهای تاریخی قبل از مرز bootstrap هیچ authority جدیدی ایجاد نمی‌کند.

## مرز زمانی

- `governance_bootstrap_effective_from = 2026-08-15`

تفسیر:

- evidence با business/effective time قبل از `2026-08-15` همچنان historical است و از این تصمیم authority prospective نمی‌گیرد.
- evidence جدید بعد از این مرز فقط در صورتی می‌تواند وارد مسیر governed شود که A2، A3، source registration و native evidence خودش را داشته باشد.

## پیشنهاد واحد برای تصمیم بعدی

اگر Governance Owner بخواهد با یک تصمیم واحد مسیر prospective را برای selected series باز کند، این بسته‌ی پیشنهادی می‌تواند مبنای همان تصمیم باشد.

### 1) شناسه پایدار pilot

- `stable_source_series_identifier = maroon_project_controls_progress_workbook_series`
- `identifier_kind = pilot_non_sensitive_series_identifier`

این شناسه:

- فقط شناسه پایدار داخلی pilot است؛
- identifier رسمی historical document control نیست؛
- historical enterprise ownership را اثبات نمی‌کند.

### 2) A2 پیشنهادی برای آینده

- `proposed_accountable_role_class = "Project Controls / PMO accountable role for future selected-series reports"`

وضعیت فعلی:

- `PROPOSED_NOT_ACTIVE`

توضیح:

- این یک role class پیشنهادی برای آینده است، نه assertion درباره historical PMO ownership.
- تا قبل از approval صریح Governance Owner و ثبت evidence لازم، هیچ designation فعالی ایجاد نمی‌شود.

### 3) A3 پیشنهادی برای آینده

- `source_report_class = project_controls_progress_workbook`
- `proposed_owning_role_class = same_as_A2_if_approved`
- `proposed_source_location_class = pilot_selected_series_controlled_reporting_workspace`
- `proposed_document_identifier_convention = future_controlled_release_identifier_required`
- `proposed_approval_method = explicit_pilot_governance_owner_selected_series_decision`

### 4) قاعده reporting/business period برای آینده

فقط این دو منبع برای business/reporting period مجاز باشند:

- `workbook_labelled_reporting_week_header`
- `designated_reporting_period_field`

و این‌ها صراحتاً غیرمجاز بمانند:

- `row_level_planned_date`
- `row_level_target_date`
- `filesystem_timestamp`
- `acquisition_timestamp`

### 5) LOW-risk fact classes مجاز

- `report_period`
- `reported_plan`
- `reported_actual`
- `reported_progress`
- `reported_activity`
- `reported_milestone`
- `reported_project_control_issue`

### 6) HIGH-risk / prohibited classes

- `contractual_delay_determination`
- `entitlement`
- `claim`
- `payment_authorization_or_status`
- `financial_liability`
- `legal_conclusion`
- `safety_or_compliance_certification`
- `final_completion`
- `current_executive_status_outside_report_period`
- `reliance_eligibility`
- `insurance_or_guarantee_status`

## اثر این تصمیم اگر approve شود

در صورت approval این بسته:

- selected series برای future records یک pilot governance boundary prospective خواهد داشت؛
- historical workbook نماینده‌ی `1402/11/21–1402/12/05` authority جدید نمی‌گیرد؛
- recordهای جدید این series فقط می‌توانند وارد مسیر governed شوند اگر:
  - source registration داشته باشند،
  - native acquisition و fingerprint و lineage داشته باشند،
  - reporting/business period را از rule مجاز بگیرند،
  - A2 و A3 prospectively برای آن‌ها برقرار باشد،
  - policy/version و integrity/conflict checks را پاس کنند.

## چیزهایی که همچنان فعال نمی‌شود

این proposal حتی در صورت approval هم به‌تنهایی این موارد را فعال نمی‌کند:

- historical authority
- historical PMO ownership
- historical document ownership
- certification
- currentness
- reliance eligibility
- automatic certification

## کوچک‌ترین تصمیم business باقی‌مانده

اگر بخواهیم فقط یک تصمیم دیگر از Governance Owner بگیریم، کوچک‌ترین تصمیم این است:

1. آیا role class پیشنهادی A2 برای future selected-series reports تأیید می‌شود؟
2. آیا controlled report definition prospective پیشنهادی A3 برای همین series تأیید می‌شود؟
3. آیا pilot identifier و effective-from boundary فوق برای همین series تأیید می‌شود؟

اگر پاسخ مثبت باشد، مرحله بعدی repository-side باید intake همان approval prospective و ساخت first post-bootstrap record contract اجرایی باشد؛ نه reinterpretation historical evidence.
