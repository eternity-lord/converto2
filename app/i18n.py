"""All user-facing translations go through this module; runtime UI rebuild enables RTL."""
LANGUAGE = 'en'
FA = {
    'Dashboard': 'داشبورد', 'MP4 Profile Fixer': 'اصلاح فایل MP4',
    'HQX Converter': 'تبدیل HQX', 'QSV Advanced': 'تنظیمات پیشرفته QSV',
    'System Tweaks': 'بهینه‌سازی سیستم', 'Logs': 'گزارش‌ها', 'Settings': 'تنظیمات',
    'Support': 'پشتیبانی', 'Encoding queue': 'صف تبدیل', 'Welcome,': 'خوش آمدی،',
    'Your studio. Faster, safer, beautifully in sync.': 'استودیوی شما؛ سریع‌تر، سازگارتر و هماهنگ.',
    'Total converted today': 'مجموع تبدیل امروز', 'TV-Compatibility Check': 'بررسی سازگاری تلویزیون',
    'Decisions powered by precision': 'تصمیم‌گیری با دقت',
    'One clean frame rate. Every screen.': 'یک نرخ فریم ثابت، برای همهٔ نمایشگرها.',
    'Analyze & Fix MP4s': 'بررسی و اصلاح MP4', 'Live queue': 'صف زنده',
    'Studio performance': 'عملکرد استودیو', 'Encoding performance': 'عملکرد تبدیل',
    'Avg speed': 'سرعت میانگین', 'GPU load': 'بار گرافیک', 'CPU load': 'بار پردازنده',
    'Space saved': 'فضای ذخیره‌شده', 'Browse': 'انتخاب پوشه', 'Add folder': 'افزودن پوشه',
    'Analyze files': 'بررسی فایل‌ها', 'Start Fix': 'شروع اصلاح', 'Stop all': 'توقف همه',
    'Start Watching': 'شروع پایش', 'Stop Watching': 'توقف پایش', 'Frame Rate': 'نرخ فریم',
    'Auto': 'خودکار', 'Custom': 'سفارشی', 'Folder': 'پوشه', 'TV preset': 'حالت تلویزیون',
    'Output': 'خروجی', 'Audio': 'صدا', 'Video': 'ویدیو', 'Profile': 'پروفایل',
    'Level': 'سطح', 'Bitrate (Mbps)': 'بیت‌ریت (مگابیت)', 'Maxrate (Mbps)': 'حداکثر بیت‌ریت',
    'Buffer (Mbps)': 'بافر (مگابیت)', 'Rate control': 'کنترل بیت‌ریت', 'Quality': 'کیفیت',
    'Conversion method': 'روش تبدیل', 'Resolution cap': 'محدودیت رزولوشن', 'FPS cap': 'سقف نرخ فریم',
    'Deinterlace': 'حذف خطوط درهم‌بافته', 'Double rate': 'نرخ دوبرابر',
    'Test with TV simulation (verify only)': 'آزمایش سازگاری تلویزیون (بدون تبدیل)',
    'Skip already TV-safe files': 'رد کردن فایل‌های سازگار',
    'Delete source only after verified success': 'حذف فایل اصلی فقط پس از تأیید موفقیت',
    'Suffix': 'پسوند نام', 'Overwrite policy': 'سیاست جایگزینی', 'FAT32 guard': 'محافظ FAT32',
    'Save settings': 'ذخیره تنظیمات', 'Search files / filter logs': 'جست‌وجوی فایل و گزارش',
    'Safe mode': 'حالت ایمن', 'Performance mode': 'حالت کارایی',
    'High priority (opt-in)': 'اولویت بالا (اختیاری)', 'Warning': 'هشدار',
    'Unverified': 'تأییدنشده', 'Blocked': 'مسدود', 'Skip analysis': 'رد کردن تحلیل',
    'Reading streams…': 'خواندن مشخصات…', 'Checking frame timing…': 'بررسی زمان‌بندی فریم…',
    'Clear finished': 'پاک کردن تمام‌شده‌ها',
    'All': 'همه', 'Info': 'اطلاعات', 'Warn': 'هشدار', 'Error': 'خطا', 'Details': 'جزئیات',
    'All files': 'همه فایل‌ها',
    'Copy': 'کپی', 'Clear': 'پاک کردن', 'Export': 'خروجی گزارش', 'Auto-scroll': 'پیمایش خودکار',
    'Pause': 'مکث', 'Resume': 'ادامه', 'Stop current': 'توقف فایل جاری', 'Skip file': 'رد کردن فایل',
    'Open output folder': 'باز کردن پوشه خروجی', 'Always on top': 'همیشه روی پنجره‌ها',
    'Auto-close when finished': 'بستن پس از اتمام', 'When finished': 'پس از اتمام',
    'Do nothing': 'هیچ کاری نکن', 'Sleep': 'خواب', 'Shut down': 'خاموش کردن',
    'Restart as administrator': 'اجرای مجدد با دسترسی مدیر', 'Show monitor': 'نمایش مانیتور',
    'Apply selected tweaks': 'اعمال بهینه‌سازی‌های انتخابی', 'Restore originals': 'بازگردانی تنظیمات اصلی',
    'Waiting': 'در انتظار', 'Analyzing': 'در حال بررسی', 'Encoding': 'در حال تبدیل',
    'Verifying': 'در حال تأیید', 'Paused': 'متوقف موقت', 'Failed': 'ناموفق', 'Skipped': 'رد شده',
    'Done': 'تمام‌شده', 'TV-Safe ✓': 'سازگار با تلویزیون ✓', 'Remove': 'حذف از صف',
    'Move to top': 'انتقال به ابتدای صف', 'Retry': 'تلاش مجدد', 'Open folder': 'باز کردن پوشه',
    'Show ffmpeg command': 'نمایش فرمان FFmpeg', 'No files yet': 'هنوز فایلی اضافه نشده',
    'Found': 'یافت‌شده', 'Elapsed': 'سپری‌شده', 'Remaining': 'باقی‌مانده', 'Finish': 'پایان',
    'Queue size': 'حجم صف', 'Ready': 'آماده', 'Encoder preset': 'پیش‌تنظیم انکودر',
    # Dashboard / shell
    'Creator workspace': 'فضای کاری سازنده', 'Studio': 'استودیو', 'Convert': 'تبدیل',
    'Tools': 'ابزارها', 'files · today': 'فایل · امروز', 'live telemetry': 'داده‌های زنده',
    'Earlier': 'پیش‌تر', 'now': 'اکنون', 'Status': 'وضعیت', 'File': 'فایل',
    'Files': 'فایل‌ها', 'QSV · probing…': 'QSV · در حال بررسی…',
    'QSV ready ✓': 'QSV آماده ✓',
    # Encoding window
    'Source / file': 'فایل مبدأ', 'Source info': 'مشخصات مبدأ',
    'Preset / output': 'حالت / خروجی', 'Progress': 'پیشرفت',
    'Preview · waiting': 'پیش‌نمایش · در انتظار', 'CPU · RAM · Temperature': 'CPU · رم · دما',
    'Target: ': 'هدف: ', 'Output (ffprobe): ': 'خروجی (ffprobe): ',
    # Settings / advanced
    'Parallel jobs': 'کارهای هم‌زمان', 'Language / زبان': 'زبان / Language',
    'NVMe / RAM disk scratch': 'پوشه موقت NVMe / رم‌دیسک',
    'Defender exclusion folder (optional)': 'پوشه استثنای Defender (اختیاری)',
    'Re-probe hardware': 'بررسی مجدد سخت‌افزار', 'Search parameter…': 'جست‌وجوی پارامتر…',
    'Auto / unsupported': 'خودکار / پشتیبانی‌نشده',
    'Only options proven by the capability probe can be enabled. TV profile, GOP, B-frames and references stay safety-locked.':
        'فقط گزینه‌هایی که آزمون سخت‌افزار تأیید کرده فعال می‌شوند. پروفایل تلویزیون، GOP، فریم‌های B و مراجع برای ایمنی قفل می‌مانند.',
    'TV mode uses AVC only. HEVC / AV1 availability is informational.':
        'حالت تلویزیون فقط از AVC استفاده می‌کند. پشتیبانی HEVC / AV1 فقط جنبه اطلاع‌رسانی دارد.',
    'Medium / slow is recommended. Veryslow may add latency with little TV-visible improvement.':
        'حالت medium یا slow توصیه می‌شود؛ veryslow فقط تأخیر را بیشتر می‌کند و بهبود محسوسی روی تلویزیون ندارد.',
    'Disabled until this exact parameter passes a hardware encode test.':
        'تا زمانی که همین پارامتر آزمون رمزگذاری سخت‌افزاری را نگذراند، غیرفعال است.',
    'Nothing is applied automatically. Changes are journaled before modification and restored on exit / next start.':
        'هیچ تغییری خودکار اعمال نمی‌شود. پیش از هر تغییر نسخه پشتیبان ثبت و هنگام خروج یا اجرای بعدی بازگردانی می‌شود.',
    'Default: one job, NORMAL priority, leave two logical cores free, 16 GPU upload frames. Free RAM <3 GB forces one job. Sustained RAM >90% / CPU >95% pauses the queue after 10 seconds in either mode.':
        'پیش‌فرض: یک کار، اولویت NORMAL، آزاد گذاشتن دو هسته منطقی و ۱۶ فریم بارگذاری GPU. اگر حافظه آزاد کمتر از ۳ گیگابایت باشد فقط یک کار اجرا می‌شود. مصرف پایدار رم بالای ۹۰٪ صف را پس از ۱۰ ثانیه متوقف می‌کند؛ فشار پردازنده فقط تعداد کارهای هم‌زمان را کاهش می‌دهد.',
    'Warning: 2–3 jobs, High priority or Performance mode can make the PC unresponsive. Changes apply to newly started jobs. Performance mode uses all encoder threads; resource guards remain enabled.':
        'هشدار: ۲ تا ۳ کار هم‌زمان، اولویت بالا یا حالت کارایی می‌تواند سیستم را کند کند. تغییرات روی کارهای جدید اثر دارد. حالت کارایی از همه رشته‌های انکودر استفاده می‌کند؛ محافظ‌های منابع فعال می‌مانند.',
    'Checking FFmpeg / QSV…': 'بررسی FFmpeg / QSV…',
    'HEVC Main (older TVs cannot play HEVC)': 'HEVC Main (تلویزیون‌های قدیمی HEVC را پخش نمی‌کنند)',
    'HEVC / AV1 require modern playback devices. CPU fallback always uses AVC for compatibility.':
        'HEVC / AV1 به دستگاه‌های پخش مدرن نیاز دارند. مسیر نرم‌افزاری برای سازگاری همیشه از AVC استفاده می‌کند.',
    'Auto selects each file’s own dominant rational cadence. Choose a fixed rate to unify the folder.':
        'حالت خودکار نرخ غالب هر فایل را جداگانه انتخاب می‌کند. برای یکسان‌سازی کل پوشه یک نرخ ثابت انتخاب کنید.',
    'Motion interpolation is CPU-intensive and may create artifacts. Integer multiples use clean duplication.':
        'درون‌یابی حرکت پرهزینه است و ممکن است آرتیفکت بسازد. ضرایب صحیح از تکرار تمیز فریم‌ها استفاده می‌کنند.',
    'Quality uses tested ICQ; if unsupported, uses explicit VBR with the selected bitrate/maxrate/buffer. Software uses CRF.':
        'کیفیت از ICQ آزموده‌شده استفاده می‌کند؛ در صورت پشتیبانی‌نشدن، VBR با بیت‌ریت/حداکثر/بافر انتخابی به کار می‌رود. مسیر نرم‌افزاری از CRF استفاده می‌کند.',
    'TV mode disables High10 / High422 / High444: only 8-bit 4:2:0 is safe.':
        'حالت تلویزیون High10 / High422 / High444 را غیرفعال می‌کند؛ فقط 8-bit 4:2:0 ایمن است.',
    'Recursive watch folder · stable size + modification time · source files preserved by default':
        'پایش بازگشتی پوشه · اندازه و زمان تغییر پایدار · حفظ فایل اصلی به‌صورت پیش‌فرض',
    'Rebuild timing. Remove unsafe streams. Deliver one verified TV-ready MP4.':
        'بازسازی زمان‌بندی، حذف جریان‌های ناامن و تحویل یک MP4 تأییدشده و آماده تلویزیون.',
    'AAC-LC · 48 kHz · stereo · 192 kbps\nAsync resampling, start-offset repair, duration verification <40 ms.\nMissing audio → silent stereo track.':
        'AAC-LC · ۴۸ کیلوهرتز · استریو · ۱۹۲ کیلوبیت\nنمونه‌برداری هم‌زمان‌سازی‌شده، اصلاح اختلاف شروع و بررسی مدت <۴۰ میلی‌ثانیه.\nنبود صدا ← ترک استریوی بی‌صدا.',
    'TV audio is always re-encoded to AAC-LC stereo 48 kHz, 192 kbps. Legacy Copy settings cannot bypass safety. Multiple audio tracks may not play on older TVs.':
        'صدای تلویزیون همیشه به AAC-LC استریو ۴۸ کیلوهرتز و ۱۹۲ کیلوبیت تبدیل می‌شود؛ تنظیم قدیمی Copy نمی‌تواند این ایمنی را دور بزند. چند ترک صوتی ممکن است در تلویزیون‌های قدیمی پخش نشود.',
    'TV simulation is a policy checker, not a physical television emulator. Playback depends on the television firmware, USB filesystem and supported codec limits.\n\nQSV availability depends on Intel hardware, drivers and the installed FFmpeg build. GPU utilisation may be unavailable without vendor performance counters.\n\nSource media is never deleted unless you explicitly select deletion and the output passes verification.':
        'شبیه‌سازی تلویزیون یک بررسی سیاستی است، نه شبیه‌ساز فیزیکی تلویزیون. پخش به سخت‌افزار تلویزیون، فایل‌سیستم USB و محدودیت‌های کدک آن بستگی دارد.\n\nپشتیبانی QSV به سخت‌افزار اینتل، درایور و نسخه FFmpeg بستگی دارد. مصرف GPU بدون شمارنده‌های کارایی سازنده ممکن است در دسترس نباشد.\n\nفایل اصلی هرگز حذف نمی‌شود مگر آنکه خودتان حذف را انتخاب کنید و خروجی تأیید شود.',
    'Designed for Mohammad Irani\nOriginal application and credit: Mohammad Irani':
        'طراحی‌شده برای محمد ایرانی\nبرنامه اصلی و اعتبار: محمد ایرانی',
    'Project on GitHub': 'پروژه در گیت‌هاب',
    '7.0 · Intel QSV / verified TV compatibility': '۷.۰ · QSV اینتل / سازگاری تأییدشده با تلویزیون',
    'Analysis complete': 'تحلیل کامل شد',
    'Active': 'فعال', 'Skipping analysis…': 'رد کردن تحلیل…',
    'Speed': 'سرعت', 'files · verified output': 'فایل · خروجی تأییدشده',
    'CPU fallback': 'پردازش نرم‌افزاری',
    'Mixed frame rates detected across files. Unify all files to: choose a fixed Frame Rate above.':
        'نرخ فریم فایل‌ها متفاوت است. برای یکسان‌سازی، یک نرخ فریم ثابت در بالا انتخاب کنید.',
    'Safety pause — see Encoding queue': 'توقف ایمنی — صف تبدیل را ببینید',
    # Options / presets
    'Same folder': 'همان پوشه', '_TV subfolder': 'زیرپوشه _TV', 'Skip': 'رد کردن',
    'Rename': 'تغییر نام', 'Replace': 'جایگزینی', 'Warn / ignore': 'هشدار / نادیده گرفتن',
    'Lower bitrate to fit': 'کاهش بیت‌ریت برای جا شدن', 'Split into parts': 'تقسیم به بخش‌ها',
    'TV-safe': 'ایمن برای تلویزیون', 'Keep all': 'حفظ همه', 'Drop / Duplicate': 'حذف / تکرار فریم',
    'Frame blend': 'ترکیب فریم', 'Motion interpolation': 'درون‌یابی حرکت', 'keep': 'حفظ',
    'Universal TV': 'تلویزیون عمومی', 'Old TV / USB 720p': 'تلویزیون قدیمی / USB ۷۲۰p',
    '4K TV': 'تلویزیون 4K', 'Phone / Tablet': 'گوشی / تبلت', 'Samsung / LG / Sony': 'سامسونگ / LG / سونی',
    'AVC compatibility · preserve source cadence up to 1080p60 · H.264 High · AAC stereo':
        'سازگاری AVC · حفظ نرخ مبدأ تا 1080p60 · H.264 High · AAC استریو',
    'Older USB players · 720p30 · Main · 8 Mbps maximum':
        'پخش‌کننده‌های USB قدیمی · 720p30 · Main · حداکثر ۸ مگابیت',
    'Modern webOS, Tizen and Android TV · up to 1080p60':
        'webOS، Tizen و Android TV مدرن · تا 1080p60',
    'H.264 High · 2160p30 · 40 Mbps maximum': 'H.264 High · 2160p30 · حداکثر ۴۰ مگابیت',
    'Portable sharing · 1080p30 · smaller files': 'اشتراک‌گذاری همراه · 1080p30 · فایل کوچک‌تر',
    'Manual profile, level and bitrate; safety checks still apply':
        'پروفایل، سطح و بیت‌ریت دستی؛ بررسی‌های ایمنی همچنان اعمال می‌شوند',
}


def set_language(value):
    global LANGUAGE
    LANGUAGE = 'fa' if value == 'fa' else 'en'


def tr(text):
    return FA.get(text, text) if LANGUAGE == 'fa' else text
