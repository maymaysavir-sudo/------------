# ארכיטקטורת סוכן — איך סוכן בנוי אצל ליאל

> תבנית-על לבניית סוכנים חדשים במערכת. נכון ל-2026-06-09.

## הרעיון המרכזי: סוכן = הגדרה + מאגר ידע

סוכן הוא לא prompt בודד. הוא צמד:
1. **קובץ הגדרה** (`<name>.md`) — אישיות, כלים, הוראות
2. **מאגר ידע** (`knowledge/`) — מה שהסוכן יודע, בקבצים נפרדים

קובץ ההגדרה דק בכוונה — כל החוכמה יושבת במאגר הידע ונקראת לפי צורך (חיסכון context).

---

## 1. מבנה פיזי + ה-symlink

כל סוכן חי בתוך פרויקט משלו, ומקושר ל-`~/.claude/agents/` כדי ש-Claude Code יגלה אותו:

```
~/.claude/agents/crazy-eva.md  ──symlink──►  projects/crazy-eva-2.0/agents/crazy-eva.md
```

החוזה: הקובץ האמיתי בפרויקט, ה-symlink הופך אותו לזמין גלובלית.

```
projects/<agent>/
├── agents/<agent>.md          ← ההגדרה (frontmatter + הוראות)
├── knowledge/
│   ├── index.md               ← אינדקס-על, מקושר ל-[[../agents/<agent>]]
│   ├── <category>/            ← ידע מקוטלג בתת-תיקיות
│   └── ...                    ← קובץ אחד = תובנה אחת
├── README.md
└── CLAUDE.md                  ← הוראות ספציפיות לפרויקט (אופציונלי)
```

---

## 2. אנטומיית קובץ הסוכן

**Frontmatter** — מנתב ומגדיר הרשאות:

```yaml
---
name: crazy-eva
role: Social media content strategist (Eva frameworks)
description: Use when Liel asks for...   # ← מחליט מתי הסוכן נקרא
tools: [Read, Write]                     # ← הרשאות הכלים
mcps: []                                 # ← אילו MCPs הסוכן מקבל
---
```

**גוף ההוראות** — תבנית קבועה לכל הסוכנים:
- **Who you are** — "אתה לא היוצר X, אתה האסטרטג של ליאל המאומן על הידע של X"
- **Before anything else** — קבצים לקרוא לפני כל פעולה: תמיד `Liel.md` + `knowledge/index.md` + הקבצים הרלוונטיים
- **Two modes** — Chat mode (שאלות/אסטרטגיה) ו-Output mode (יצירת תוצר)
- **Rules** — גבולות גזרה ("תמיד מבוסס על מאגר הידע, אחרת תגיד שחסר")
- **Knowledge link** — `[[../knowledge/index]]`

---

## 3. מאגר הידע — קובץ אחד = תובנה אחת

כל קובץ ידע באותו פורמט קבוע:

```markdown
# כותרת התובנה
**Source**: <לינק למקור>
**Category**: <category>
**Added**: 2026-04-07

## Core Insight     ← התובנה במשפט
## How It Works     ← הפירוק
## Example          ← דוגמה מוחשית
## When to Use      ← מתי להשתמש
```

ה-`index.md` הוא הכניסה היחידה — שורה אחת לכל קובץ עם hook קצר. הסוכן קורא קודם אינדקס זול, ואז רק את הקבצים שצריך.

---

## 4. שני סוגי סוכנים (ארכיטיפים)

| | סוכן-פרסונה (מאומן על יוצר) | סוכן-מפעיל (כלי עבודה) |
|---|---|---|
| דוגמאות | crazy-eva, claudette, hormozi, garchik, annie-pistachio, codiz | gigly, mutato, sendoval, mekano, airti, liloo, architext, librarian, ewob |
| מקור הידע | חילוץ מסרטונים | conventions.md + account-map.md + playbooks/ |
| MCPs | אין (Read/Write בלבד) | יש (meta-ads, sendpulse, make, airtable...) |
| איך מתמלא | סקיל חילוץ (`/crazy-eva <לינק>`) + `/process-queue` | ידני / playbooks |

---

## 5. הצמד סוכן ↔ סקיל-חילוץ

לסוכני-הפרסונה יש סקיל תואם (`/crazy-eva`, `/claudette`, `/hormozi`). הסקיל הוא המפעל של מאגר הידע:

```
לינק לסרטון → /crazy-eva → מחלץ תובנה → כותב knowledge/<category>/<slug>.md → מעדכן index.md
```

הסוכן **קורא** מהמאגר; הסקיל **כותב** אליו. הפרדת תפקידים.

---

## בקצרה — שכבות המערכת

```
description (frontmatter)   →  ניתוב: מתי הסוכן נקרא
tools + mcps               →  יכולות והרשאות
גוף ההוראות               →  אישיות + workflow (Before anything / Two modes / Rules)
knowledge/index.md         →  שער הידע (זול לקריאה)
knowledge/**/*.md          →  הידע עצמו (תובנה לקובץ)
סקיל החילוץ /<name>        →  מה שמזין את המאגר
symlink → ~/.claude/agents  →  מה שהופך הכל לזמין
```

---

## צ'קליסט לבניית סוכן חדש

1. `mkdir -p projects/<agent>/{agents,knowledge}`
2. כתוב `agents/<agent>.md` — frontmatter (name/role/description/tools/mcps) + גוף ההוראות לפי התבנית
3. צור `knowledge/index.md` עם לינק `[[../agents/<agent>]]`
4. למפעיל: הוסף `conventions.md` + `account-map.md` (+ `playbooks/`); לפרסונה: צור סקיל חילוץ תואם
5. symlink: `ln -s "$PWD/projects/<agent>/agents/<agent>.md" ~/.claude/agents/<agent>.md`
6. עדכן את ה-description של הסוכן ב-FleetView / רשימת ה-subagents
