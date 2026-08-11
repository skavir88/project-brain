# بسته درخواست واقعی ST1-134 برای دو ورودی selected-series

## موضوع

برای ادامه مسیر واقعی ST1-066 فقط دو ورودی واقعی و محدود لازم است، هر دو
مربوط به همین series مشخص:

- series هدف: `maroon_project_controls_progress_workbook_series`
- نمونه نماینده شناخته‌شده: `070-TWRP-24 1402-12-05.xlsx`
- دوره گزارش نمونه شناخته‌شده: `1402/11/21–1402/12/05`

این درخواست فقط برای همین series است و به هیچ source boundary جدیدی گسترش
نمی‌یابد.

## هدف این بسته

هدف این بسته این نیست که:

- delegation واقعی را فعال کند،
- source را register کند،
- native acquisition واقعی را اجرا کند،
- policy decision واقعی را اجرا کند،
- certification انجام دهد،
- یا current status پروژه را اعلام کند.

هدف فقط این است که دو artifact واقعی موردنیاز برای ورود به
`independent controlled review` به‌صورت روشن و قابل‌ارسال مشخص شوند.

## دو ورودی واقعی موردنیاز

### ورودی 1 — Governance / Report-Definition Bundle

یک bundle واقعی و sanitize‌شده برای همین series که این چهار مؤلفه را پوشش دهد:

1. A1 — تأیید نقش حاکمیتی مجاز
2. A2 — تأیید نقش مسئول Project Controls / PMO
3. A3 — تعریف کنترل‌شده همین کلاس report/workbook
4. شناسه پایدار non-sensitive برای همین source/reporting series

این ورودی باید روشن کند:

- چه role سازمانی scope این pilot را برای این کلاس گزارش می‌تواند تأیید کند؛
- چه role سازمانی مسئول رسمی recurring Project Controls workbook/report class است؛
- reporting period رسمی دقیقاً در کدام header/field تعریف می‌شود؛
- convention کنترل/انتشار/نسخه این کلاس چیست؛
- شناسه پایدار non-sensitive این series چیست.

### ورودی 2 — Native Record Artifact

یک artifact واقعی و sanitize‌شده برای یک record واقعی از همین series که
حداقل این اطلاعات را داشته باشد:

- `source_id` = `maroon_project_controls_progress_workbook_series`
- نوع منبع / source type
- non-sensitive location class
- owning role class
- acquisition metadata
- original fingerprint
- deterministic transformation lineage
- resolved business/reporting time
- policy context
- independent-verification flags/reference fields

این artifact باید برای همین series باشد، نه یک workbook از source یا scope دیگر.

## حداقل اطلاعات لازم برای ورودی 1

### A1

- نام و نام خانوادگی امضاکننده
- سمت سازمانی
- role حاکمیتی مورد تأیید
- مبنای اختیار
- تاریخ اثر
- روش تأیید

### A2

- نام و نام خانوادگی امضاکننده
- سمت سازمانی
- role مسئول
- دامنه پروژه
- شرح مسئولیت رسمی recurring reporting
- تاریخ اثر
- روش تأیید

### A3

- نام کلاس گزارش/کاربرگ
- role مالک سازمانی
- نوع محل/سامانه نگهداری
- محل قطعی ثبت reporting period
- rule شناسایی نسخه / revision / document number
- rule انتشار / issue / approval
- تاریخ اثر
- روش تأیید

### شناسه پایدار series

یکی از این‌ها کافی است:

- کد رسمی series
- شناسه document-control series
- شناسه report family
- یا هر identifier داخلی پایدار که همین series را بدون افشای مسیر محرمانه
  مشخص کند

## حداقل اطلاعات لازم برای ورودی 2

برای یک record واقعی از همین series:

- source id
- media type
- acquisition method
- acquisition timestamp
- original SHA-256 fingerprint
- size bytes
- read-only بودن acquisition
- transformation type / tool / version / transformed_at
- input fingerprint
- output fingerprint
- deterministic = true
- lineage_complete = true
- reporting/business period
- resolution source برای business time
- policy id / policy version / risk tier

## قواعد مهم

### قاعده 1 — business time

business/reporting time نباید از این‌ها گرفته شود:

- filesystem timestamp
- acquisition timestamp
- row-level planned date
- row-level target date

business/reporting time فقط باید از:

- header دارای reporting week / reporting period
- یا field رسمی و مشخص reporting period

بیاید.

### قاعده 2 — scope

هر دو artifact باید فقط برای همین selected series باشند:

- `maroon_project_controls_progress_workbook_series`

### قاعده 3 — عدم افشای محرمانگی

در نسخه‌ای که برای repository/local validation می‌آید:

- secret نفرستید
- password نفرستید
- token نفرستید
- private path حساس نفرستید
- raw confidential content غیرلازم نفرستید

در صورت نیاز، شناسه‌ها و locators باید sanitize یا non-sensitive باشند.

## چیزهایی که هنوز با این دو ورودی هم فعال نمی‌شوند

حتی بعد از دریافت این دو artifact هم این‌ها خودکار فعال نمی‌شوند:

- delegation activation
- source registration
- native acquisition execution
- policy mutation
- certification
- current executive status
- reliance eligibility
- insurance semantics

## خروجی مورد انتظار بعد از دریافت این دو ورودی

اگر هر دو artifact:

- exact-scope باشند،
- structurally acceptable باشند،
- و با boundaryهای selected series منطبق باشند،

آنگاه step بعدی فقط این خواهد بود:

`begin_independent_controlled_review`

نه بیشتر.

## متن کوتاه قابل ارسال

> برای ادامه pilot فقط دو artifact واقعی و sanitize‌شده برای همین series لازم است:
>
> 1. یک governance/report-definition bundle برای `maroon_project_controls_progress_workbook_series` که A1/A2/A3 و شناسه پایدار non-sensitive series را پوشش دهد.
> 2. یک native-record artifact واقعی برای یک record از همین series که acquisition metadata، fingerprint، transformation lineage و reporting/business time را نشان دهد.
>
> لطفاً فقط همین دو artifact را برای همین series آماده کنید. این درخواست به معنی activation، certification یا current-status declaration نیست.
