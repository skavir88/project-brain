# بسته درخواست دقیق ST1-136 برای ورودی‌های باقی‌مانده selected-series

## وضعیت فعلی

برای مسیر واقعی ST1-066 روی همان series هدف:

- `target_source_id`: `maroon_project_controls_progress_workbook_series`
- workbook نماینده شناخته‌شده: `070-TWRP-24 1402-12-05.xlsx`
- نمونه دوره گزارش مشاهده‌شده در خود سند: `1402/11/21–1402/12/05`

اکنون فقط **A1** به‌صورت evidence واقعی دریافت شده است و همان هم هنوز فقط
`SUPPLIED_UNVALIDATED_REAL_EVIDENCE` است.

A1 فقط این را پوشش می‌دهد:

- نقش حاکمیتی مجاز برای pilot governance محدود SDAS / Data Insurance

A1 **این‌ها را ایجاد نمی‌کند**:

- authority تاریخی Project Controls
- authority مالکیت source
- authority اسناد تاریخی
- authority همین Maroon workbook series
- current project status
- certification
- reliance eligibility

بنابراین برای ورود به `independent controlled review` هنوز فقط ورودی‌های زیر
باقی مانده‌اند.

## فقط چهار ورودی واقعی باقی‌مانده

### 1) A2 — تأیید نقش مسئول Project Controls / PMO

باید روشن کند:

- کدام role سازمانی مسئول رسمی recurring Project Controls progress
  workbook/report class برای Maroon pilot است؛
- این role مسئول تهیه/کنترل/انتشار همین کلاس گزارش است؛
- دامنه این مسئولیت دقیقاً همین پروژه/series را پوشش می‌دهد؛
- تاریخ اثر این مسئولیت چیست.

حداقل اطلاعات لازم:

- نام و نام خانوادگی امضاکننده
- سمت سازمانی امضاکننده
- نام role مسئول
- دامنه پروژه
- شرح مسئولیت رسمی role
- تاریخ اثر
- روش تأیید

### 2) A3 — تعریف controlled report/workbook class

باید روشن کند:

- نام همین کلاس گزارش/کاربرگ چیست؛
- role مالک سازمانی آن چیست؛
- نوع محل/سامانه نگهداری آن چیست؛
- reporting period رسمی دقیقاً در کدام header یا field ثبت می‌شود؛
- convention نسخه / revision / document number چیست؛
- rule انتشار / issue / approval چیست؛
- تاریخ اثر این تعریف چیست.

حداقل اطلاعات لازم:

- نام کلاس گزارش/کاربرگ
- role مالک سازمانی
- نوع محل/سامانه نگهداری
- محل قطعی ثبت reporting period
- rule شناسایی نسخه / revision / document number
- rule انتشار / issue / approval
- تاریخ اثر
- روش تأیید

### 3) stable source-registration evidence reference

باید یک reference غیرمحرمانه و پایدار بدهد که نشان دهد evidence مربوط به
source registration همین series از کجا ارجاع‌پذیر است.

نمونه‌های قابل‌قبول:

- reference یک attestation/signed confirmation
- reference یک controlled internal record
- reference یک document-control identifier غیرمحرمانه

این مورد نباید secret یا raw confidential path باشد.

### 4) stable non-sensitive source series identifier

باید یک identifier پایدار غیرمحرمانه برای همین reporting series بدهد.

نمونه‌های قابل‌قبول:

- کد رسمی series
- شناسه document-control series
- شناسه report family
- هر identifier داخلی پایدار که همین series را بدون افشای locator محرمانه
  مشخص کند

## Native record artifact باقی‌مانده

علاوه بر چهار ورودی بالا، هنوز **یک native-record artifact واقعی sanitize‌شده**
برای همین selected series لازم است.

حداقل باید این‌ها را نشان دهد:

- `source_id = maroon_project_controls_progress_workbook_series`
- source type
- non-sensitive location class
- acquisition metadata
- original fingerprint
- deterministic transformation lineage
- resolved reporting/business time
- policy context

## قواعدی که تغییر نکرده‌اند

### business time

business/reporting time فقط باید از این‌ها بیاید:

- header دارای reporting week / reporting period
- field رسمی و مشخص reporting period

این‌ها معتبر نیستند:

- filesystem timestamp
- acquisition timestamp
- row-level planned date
- row-level target date

### scope

همه ورودی‌ها فقط باید برای همین selected series باشند:

- `maroon_project_controls_progress_workbook_series`

### boundary

حتی بعد از دریافت این ورودی‌ها هم هنوز این‌ها خودکار فعال نمی‌شوند:

- delegation activation
- source registration execution
- native acquisition execution
- policy mutation
- certification
- current executive status
- reliance eligibility

## خروجی مورد انتظار بعد از دریافت این ورودی‌ها

اگر:

- A2 و A3 و source-registration evidence reference و stable series identifier
  برسند،
- و native-record artifact هم برای همین selected series برسد،
- و هر دو gateهای exact-scope را pass کنند،

آن‌گاه step بعدی فقط این خواهد بود:

`begin_independent_controlled_review`

نه بیشتر.

## متن کوتاه قابل‌ارسال

> برای ادامه مسیر واقعی ST1-066 روی series
> `maroon_project_controls_progress_workbook_series`، A1 دریافت شده اما هنوز
> کافی نیست. لطفاً فقط این موارد را برای همین series مشخص کنید:
>
> 1. A2: چه role سازمانی مسئول رسمی recurring Project Controls progress
>    workbook/report class برای Maroon pilot است؟
> 2. A3: reporting period رسمی همین کلاس گزارش دقیقاً در کدام header/field
>    ثبت می‌شود و convention کنترل/انتشار آن چیست؟
> 3. یک stable source-registration evidence reference غیرمحرمانه
> 4. یک stable non-sensitive source series identifier
> 5. یک native-record artifact sanitize‌شده برای یک record واقعی از همین
>    series
>
> این درخواست به معنی activation، certification یا current-status declaration
> نیست.
