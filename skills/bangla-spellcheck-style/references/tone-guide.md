# Bangla tone, register and usage guide

## Register: চলিত, not সাধু

Modern web, app and marketing text uses চলিত (standard colloquial). সাধু (the older literary
register) survives in some legal documents, old literature and a few formal notices. Mixing
them in one text is a classic error (গুরুচণ্ডালী দোষ).

| সাধু | চলিত |
| --- | --- |
| তাহার, তাহাকে, তাহারা | তার, তাকে, তারা |
| যাহা, যাহার | যা, যার |
| ইহা, উহা | এটা / এটি, ওটা / ওটি |
| করিয়া, করিয়াছে, করিতেছে | করে, করেছে, করছে |
| হইয়া, হইয়াছে, হইবে | হয়ে, হয়েছে, হবে |
| বলিল, বলিলেন | বলল, বললেন |
| গিয়াছে | গেছে / গিয়েছে |
| হইতে | থেকে |

## Address: আপনি, তুমি, তুই

| Form | Use for | Verb (imperative) | Example |
| --- | --- | --- | --- |
| আপনি (formal) | apps, banking, government, e-commerce, support, most marketing | -উন: করুন, দেখুন, দিন, যান | আপনার পাসওয়ার্ড লিখুন |
| তুমি (familiar) | youth brands, games, kids' apps, friendly chat (only if the brand voice says so) | -ও: করো, দেখো, দাও, যাও | তোমার স্কোর দেখো |
| তুই (intimate) | never in product text | | |

Rules:
- One form per product. Do not switch from আপনি in buttons to তুমি in error messages.
- Third person respectful: তিনি, তাঁর, তাঁরা (with chandrabindu) for people; সে, তার for
  neutral or familiar.
- Impersonal instructions avoid the pronoun: "পাসওয়ার্ড দিন", "ফাইল নির্বাচন করুন".
- Polite requests: অনুগ্রহ করে / দয়া করে sparingly; one per screen is enough.

The checker's `--tone formal` flags তুমি/তোমার/তোমাকে/তোমরা/তোমাদের/তুই/তোর/তোকে and
informal imperatives (করো, দেখো, যাও, দাও, চলো, বলো, লেখো, খোলো, রাখো, নাও, এসো, শোনো, পড়ো).

## Common usage questions

| Question | Rule | Examples |
| --- | --- | --- |
| কি or কী? | কি for yes/no questions (particle); কী for "what" (pronoun/adjective) and exclamations | তুমি কি যাবে? / তুমি কী খাবে? / কী সুন্দর! |
| কোন or কোনো? | কোন = which; কোনো = any | কোন বইটা? / কোনো সমস্যা নেই |
| হল or হলো? | হলো (past "became") is the Academy form; হল = hall (noun) | কাজ শেষ হলো |
| কেন / কেনো | কেন (why) | |
| মতো / মত | মতো = like; মত = opinion | তোমার মতো / আমার মত |
| এ / এই | both fine; এই is clearer in UI | |
| টি / টা | টি is more formal; টা colloquial | ৩টি পণ্য |

## Numbers in prose

- Small numbers in running text can be words (দুই জন, তিনটি) or digits; be consistent.
- Use digits for prices, dates, measurements and anything users compare.
- Do not mix Bangla and Latin digits on the same page unless there is a reason (model
  numbers, codes).

## Punctuation

| Mark | Rule |
| --- | --- |
| । (danda, U+0964) | ends statements; never `.` or `|` |
| ? ! | as in English |
| , ; : | as in English, no space before |
| quotes | straight or curly quotation marks, one style per product |
| … | three dots or the ellipsis character, consistently |
| - and – | hyphen joins words (ঢাকা-চট্টগ্রাম), en dash for ranges (১০–২০) |

No space before punctuation and one space after it, as in: "কাজ শেষ। এবার বিশ্রাম।"

## UI microcopy patterns

| Situation | Pattern | Example |
| --- | --- | --- |
| Button | verb + করুন | অর্ডার করুন, সংরক্ষণ করুন |
| Success | passive past | পরিবর্তন সংরক্ষণ করা হয়েছে। |
| Error | what happened + what to do | সংযোগ বিচ্ছিন্ন হয়েছে। আবার চেষ্টা করুন। |
| Empty state | statement + action | আপনার কার্ট খালি। কেনাকাটা শুরু করুন। |
| Confirmation | question with কি | আপনি কি এই অর্ডারটি বাতিল করতে চান? |
| Field hint | imperative or example | আপনার মোবাইল নম্বর লিখুন (যেমন ০১৭১১-০০০০০০) |

## Marketing copy

- Short, concrete, local: "ঢাকার ভেতরে ২৪ ঘণ্টায় ডেলিভারি" beats generic superlatives.
- Banglish or English words are fine where audiences use them (অফার, ক্যাশব্যাক), but keep
  spelling consistent (`bangla-ui-translation` glossary).
- Avoid literal translation of English idioms; rewrite the idea.
