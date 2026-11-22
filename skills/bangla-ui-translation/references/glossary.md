# Bangla UI glossary and style rules

A starting glossary for Bangladeshi software (bn-BD). Where two forms are common, the first
is the recommended default for apps and websites; the second is fine if a product already
uses it. Keep one choice per product and record it in the product's own glossary.

## Style rules

| Rule | Example |
| --- | --- |
| Formal address by default: আপনি + -উন imperative | Save -> সংরক্ষণ করুন, Enter your name -> আপনার নাম লিখুন |
| Buttons are verbs; short nav labels may be nouns | Delete -> মুছে ফেলুন; Settings -> সেটিংস |
| Sentences end with the danda `।` (U+0964) | Saved. -> সংরক্ষণ করা হয়েছে। |
| Keep `?`, `!`, `,` and `:` as in English | Are you sure? -> আপনি কি নিশ্চিত? |
| Classifiers attach to numbers | 3 items -> `{count}টি পণ্য`; 5 people -> `%dজন` |
| Use চলিত (standard colloquial), never সাধু, in UI | হয়েছে, not হইয়াছে |
| Prefer the word users search for | অ্যাকাউন্ট over হিসাব for a login account |
| Loanwords follow Bangla Academy spelling | অ্যাপ (not এ্যাপ), পোস্ট (not পোষ্ট), স্টোর (not ষ্টোর) |
| Do not translate brand names, product names, file formats, units | bKash, Wi-Fi, PDF, GB |
| Passive "has been done" forms sound natural for status messages | Order placed -> অর্ডার গ্রহণ করা হয়েছে |
| Avoid literal calques | "Hit the button" -> বাটনে ক্লিক করুন (not বাটনে আঘাত করুন) |
| Errors: say what happened and what to do | ইন্টারনেট সংযোগ নেই। আবার চেষ্টা করুন। |

## Placeholder and markup rules

- Never translate, re-case or re-number placeholders: `{name}`, `{{name}}`, `%s`, `%1$s`,
  `%(name)s`, `:name`, `$t(key)`, `<0>`, `<strong>`.
- Never use Bangla digits inside placeholders (`%১$s` breaks printf).
- Reorder positional placeholders freely when word order changes (`%2$s ... %1$s`).
- Keep HTML attributes untouched: `<a href="{url}">` stays exactly the same; translate only
  the link text.
- A space usually separates a placeholder from the next word, except for classifiers and
  case endings attached to the value (`{name}-এর` or `{name}এর`; pick one style).

## Glossary

| English | Bangla | Notes |
| --- | --- | --- |
| Home | হোম / প্রথম পাতা | |
| Settings | সেটিংস | |
| Profile | প্রোফাইল | |
| Account | অ্যাকাউন্ট | |
| Dashboard | ড্যাশবোর্ড | |
| Notifications | বিজ্ঞপ্তি / নোটিফিকেশন | |
| Messages | বার্তা / মেসেজ | |
| Search | খুঁজুন / অনুসন্ধান | button: খুঁজুন; field label: অনুসন্ধান |
| Search results | অনুসন্ধানের ফলাফল | |
| Save | সংরক্ষণ করুন | |
| Save changes | পরিবর্তন সংরক্ষণ করুন | |
| Cancel | বাতিল করুন / বাতিল | |
| Delete | মুছে ফেলুন | |
| Remove | সরিয়ে ফেলুন | |
| Edit | সম্পাদনা করুন | |
| Add | যোগ করুন | |
| Create | তৈরি করুন | |
| Update | হালনাগাদ করুন / আপডেট করুন | |
| Submit | জমা দিন | |
| Send | পাঠান | |
| Confirm | নিশ্চিত করুন | |
| Continue | চালিয়ে যান | |
| Next | পরবর্তী | |
| Previous | পূর্ববর্তী | |
| Back | ফিরে যান | |
| Skip | এড়িয়ে যান | |
| Close | বন্ধ করুন | |
| Open | খুলুন | |
| Done | সম্পন্ন | |
| OK | ঠিক আছে | |
| Yes / No | হ্যাঁ / না | |
| Apply | প্রয়োগ করুন | |
| Reset | রিসেট করুন | |
| Retry / Try again | আবার চেষ্টা করুন | |
| Refresh | রিফ্রেশ করুন | |
| Copy | কপি করুন | |
| Copied | কপি করা হয়েছে | |
| Paste | পেস্ট করুন | |
| Undo | পূর্বাবস্থায় ফেরান | |
| Share | শেয়ার করুন | |
| Download | ডাউনলোড করুন | |
| Upload | আপলোড করুন | |
| Print | প্রিন্ট করুন | |
| Filter | ফিল্টার | |
| Sort by | সাজান | |
| Select | নির্বাচন করুন | |
| Select all | সব নির্বাচন করুন | |
| All | সব / সকল | |
| None | কোনোটি নয় | |
| More | আরও | |
| Show more | আরও দেখুন | |
| Read more | আরও পড়ুন | |
| View | দেখুন | |
| Details | বিস্তারিত | |
| Sign in / Log in | সাইন ইন করুন / লগ ইন করুন | pick one product-wide |
| Sign up / Register | সাইন আপ করুন / নিবন্ধন করুন | |
| Log out | লগ আউট | |
| Forgot password? | পাসওয়ার্ড ভুলে গেছেন? | |
| Password | পাসওয়ার্ড | |
| Confirm password | পাসওয়ার্ড নিশ্চিত করুন | |
| Username | ব্যবহারকারীর নাম | |
| Email | ইমেইল | |
| Phone / Mobile number | মোবাইল নম্বর / ফোন নম্বর | Bangladesh: মোবাইল নম্বর is the common label |
| Verification code / OTP | যাচাইকরণ কোড / ওটিপি | |
| Verify | যাচাই করুন | |
| Name | নাম | |
| Full name | পুরো নাম | |
| Address | ঠিকানা | |
| District | জেলা | Bangladesh address field |
| Division | বিভাগ | |
| Upazila / Thana | উপজেলা / থানা | |
| Post code | পোস্ট কোড | |
| Date of birth | জন্মতারিখ | |
| Gender | লিঙ্গ | |
| Language | ভাষা | |
| Date | তারিখ | |
| Time | সময় | |
| Today | আজ | |
| Yesterday | গতকাল | |
| Tomorrow | আগামীকাল | |
| Cart | কার্ট | |
| Add to cart | কার্টে যোগ করুন | |
| Checkout | চেকআউট | |
| Order | অর্ডার | |
| Place order | অর্ডার করুন | |
| Order history | অর্ডারের ইতিহাস | |
| Track order | অর্ডার ট্র্যাক করুন | |
| Payment | পেমেন্ট / অর্থ পরিশোধ | |
| Pay now | এখনই পেমেন্ট করুন | |
| Cash on delivery | ক্যাশ অন ডেলিভারি | |
| Price | দাম / মূল্য | মূল্য is more formal |
| Discount | ছাড় | |
| Free | বিনামূল্যে / ফ্রি | free shipping: ফ্রি ডেলিভারি |
| Delivery | ডেলিভারি | |
| Delivery charge | ডেলিভারি চার্জ | |
| Quantity | পরিমাণ | |
| Subtotal | উপমোট | |
| Total | মোট | |
| VAT | ভ্যাট | |
| In stock / Out of stock | স্টকে আছে / স্টকে নেই | |
| Coupon code | কুপন কোড | |
| Invoice | ইনভয়েস / চালান | |
| Refund | ফেরত / রিফান্ড | |
| Help | সাহায্য | |
| Support | সহায়তা | |
| Contact us | যোগাযোগ করুন | |
| About us | আমাদের সম্পর্কে | |
| FAQ | সাধারণ জিজ্ঞাসা | |
| Privacy policy | গোপনীয়তা নীতি | |
| Terms and conditions | শর্তাবলি | |
| Cookie | কুকি | |
| Comment | মন্তব্য | |
| Reply | উত্তর দিন | |
| Like | পছন্দ | |
| Follow | অনুসরণ করুন | |
| Subscribe | সাবস্ক্রাইব করুন | |
| Report | রিপোর্ট করুন | |
| Loading... | লোড হচ্ছে... | |
| Please wait | অনুগ্রহ করে অপেক্ষা করুন | |
| Error | ত্রুটি | |
| Something went wrong | কিছু একটা সমস্যা হয়েছে | |
| Warning | সতর্কতা | |
| Success | সফল | |
| Required | আবশ্যক | form field marker |
| Optional | ঐচ্ছিক | |
| Invalid | অবৈধ / সঠিক নয় | "Invalid email" -> ইমেইল ঠিকানাটি সঠিক নয় |
| No results found | কোনো ফলাফল পাওয়া যায়নি | |
| Are you sure? | আপনি কি নিশ্চিত? | |
| This action cannot be undone | এই কাজটি আর ফেরানো যাবে না | |
| Version | সংস্করণ | |
| File / Folder | ফাইল / ফোল্ডার | |
| Image / Video | ছবি / ভিডিও | |

## Review checklist

- [ ] Same keys, same order, same nesting as the source file
- [ ] `check_placeholders.py` exits 0
- [ ] One term per concept across the whole product (glossary applied)
- [ ] Tone consistent (no তুমি in an আপনি product)
- [ ] Danda `।` at sentence ends; no `.` or `|`
- [ ] Spelling checked with `bangla-spellcheck-style`
- [ ] Strings viewed in the real UI: Bangla is often 20-40% longer than English; check
      buttons and table headers for truncation
