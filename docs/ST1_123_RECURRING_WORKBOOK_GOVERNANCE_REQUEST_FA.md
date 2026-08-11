# بسته درخواست کسب‌وکاری ST1-123

## موضوع

فعال‌سازی حداقل governance قابل‌استفاده برای این کلاس مشخص:

- پروژه: Maroon pilot
- کلاس منبع: کاربرگ/گزارش دوره‌ای پیشرفت Project Controls
- series هدف: `maroon_project_controls_progress_workbook_series`
- نمونه واقعی نماینده در شواهد موجود: `070-TWRP-24 1402-12-05.xlsx`
- دوره گزارش مشاهده‌شده در خود سند: `1402/11/21–1402/12/05`

## هدف این درخواست

هدف این بسته این نیست که:

- ST1-061 را اصلاح کند،
- certification انجام دهد،
- current status پروژه را اعلام کند،
- یا هیچ authority تاریخی را به‌صورت retroactive ایجاد کند.

هدف فقط این است که کوچک‌ترین bundle قابل‌استفاده و reusable برای این series
مشخص فراهم شود تا سیستم بتواند در گام بعدی:

- source واقعی را register کند،
- source-control را verify کند،
- native acquisition را انجام دهد،
- business time را از rule مجاز resolve کند،
- و یک record واقعی را تا `policy_automatic` hard stop برساند،

بدون اینکه certification خودکار انجام شود.

## چه چیزهایی هنوز لازم است

برای همین series فقط این 4 ورودی لازم است:

1. A1 — تأیید نقش حاکمیتی مجاز
2. A2 — تأیید نقش مسئول Project Controls / PMO
3. A3 — تعریف کنترل‌شده همین کلاس report/workbook
4. یک شناسه پایدار non-sensitive برای source/reporting series

## فرم 1 — A1

### سؤال

چه role سازمانی مجاز است scope حاکمیتی این pilot را برای همین کلاس
`Project Controls progress workbook/report` تصویب کند؟

### خروجی قابل‌قبول

یک سند کنترل‌شده یا تأیید امضاشده که روشن کند:

- نام role حاکمیتی چیست،
- مبنای اختیار آن role چیست،
- این اختیار از چه تاریخی معتبر است،
- و این اختیار همین scope را پوشش می‌دهد.

### حداقل اطلاعات لازم

- نام و نام خانوادگی امضاکننده
- سمت سازمانی
- role حاکمیتی مورد تأیید
- مبنای اختیار
- تاریخ اثر
- روش تأیید

## فرم 2 — A2

### سؤال

کدام role سازمانی مسئول رسمی recurring Project Controls progress
workbook/report class برای پروژه Maroon است؟

### خروجی قابل‌قبول

یک سند کنترل‌شده یا تأیید امضاشده که روشن کند:

- role مسئول چیست،
- این role همین پروژه را پوشش می‌دهد،
- و مسئولیت رسمی تهیه/کنترل/انتشار همین کلاس گزارش با اوست.

### حداقل اطلاعات لازم

- نام و نام خانوادگی امضاکننده
- سمت سازمانی
- نام role مسئول
- دامنه پروژه
- شرح مسئولیت رسمی
- تاریخ اثر
- روش تأیید

## فرم 3 — A3

### سؤال

برای همین کلاس `Project Controls progress workbook/report`، دوره گزارش رسمی
دقیقاً در کدام header یا field تعریف می‌شود و convention کنترل/انتشار آن چیست؟

### خروجی قابل‌قبول

یک سند کنترل‌شده یا تأیید امضاشده که روشن کند:

- نام کلاس گزارش/کاربرگ چیست،
- role مالک سازمانی آن چیست،
- نوع محل/سامانه نگهداری چیست،
- reporting period دقیقاً در کدام header یا field تعریف می‌شود،
- convention شناسایی نسخه / revision / document number چیست،
- و rule انتشار / issue / approval چیست.

### حداقل اطلاعات لازم

- نام کلاس گزارش/کاربرگ
- role مالک سازمانی
- نوع محل/سامانه نگهداری
- محل قطعی ثبت reporting period
- rule شناسایی نسخه / revision / document number
- rule انتشار / issue / approval
- تاریخ اثر
- روش تأیید

## ورودی چهارم — شناسه پایدار source series

علاوه بر A1/A2/A3، برای register کردن source واقعی، فقط یک شناسه پایدار
non-sensitive لازم است که این series را مشخص کند.

این شناسه می‌تواند یکی از این‌ها باشد:

- کد رسمی series
- شناسه document-control series
- شناسه report family
- یا هر identifier داخلی پایدار که همین series را بدون افشای مسیر محرمانه مشخص کند

## قاعده مهم business time

برای این کلاس، این‌ها business/reporting time معتبر نیستند:

- تاریخ فایل
- زمان acquisition
- تاریخ‌های row-level برنامه‌ای

business/reporting time فقط باید از یکی از این دو بیاید:

- header دارای reporting week / reporting period
- field رسمی و مشخص reporting period

## چیزهایی که با این bundle فعال نمی‌شوند

حتی بعد از دریافت این bundle هم این‌ها خودکار فعال نمی‌شوند:

- certification
- current executive status
- reliance eligibility
- insurance semantics
- authority تاریخی برای records قبلی

## متن کوتاه قابل ارسال برای همکار مسئول

> برای series مربوط به گزارش/کاربرگ دوره‌ای پیشرفت Project Controls در پروژه Maroon،
> لطفاً فقط این 4 مورد را با سند کنترل‌شده یا تأیید امضاشده مشخص کنید:
>
> 1. چه role سازمانی مجاز است scope حاکمیتی این pilot را برای این کلاس گزارش تصویب کند؟
> 2. چه role سازمانی مسئول رسمی همین recurring Project Controls workbook/report class است؟
> 3. در همین کلاس گزارش، reporting period رسمی دقیقاً در کدام header/field تعریف می‌شود و convention کنترل/انتشار آن چیست؟
> 4. شناسه پایدار non-sensitive این source/reporting series چیست؟

