# Meta Ads: account → client mapping

Read by the `optimize-ads` skill to attribute ad spend to the right client or project.

**Status: not filled in yet.** The rows below are the schema, not data. Until real
account IDs are entered here, `optimize-ads` cannot attribute spend, and it must say so
rather than guess. Do not invent an Account ID.

## How to fill it

Account IDs come from Meta Business Manager, or from the MCP:
`get_ad_accounts` on the meta-ads MCP lists every account the token can reach.

| חשבון | Account ID | יעד | מצב |
|---|---|---|---|
| _(display name in BM)_ | `act_XXXXXXXXXX` | _(client or project this spend belongs to)_ | A |

### עמודות
- **חשבון** - the account name as it appears in Business Manager
- **Account ID** - the `act_` prefixed numeric ID. This is the join key
- **יעד** - which client or project the spend is attributed to. Several accounts may map to one יעד
- **מצב** - `A` = active, spend expected. `B` = dormant or archived, spend is historical only

### כללים
- One row per ad account. Never merge two accounts into one row
- An account with no `יעד` is unattributed. `optimize-ads` must report its spend separately, never fold it into another client's ROAS
- When an account changes hands, add a new row and mark the old one `B`. Do not overwrite history
