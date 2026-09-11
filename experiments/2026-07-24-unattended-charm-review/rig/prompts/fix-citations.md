A mechanical check of your review found citations whose line numbers do not match the
code they quote. This is checked, not guessed: for each one below, the quoted text was
searched for in the file and found somewhere else.

$REPORT

Citations are checked against `$WS/repo` **and** `$WS/deps` (the charm's unpacked
dependencies), so a citation into a `single_kernel_*` or similar package is checkable and
should carry a real line number. "no such file" means the path is wrong or invented in
both places — not that the file is merely outside the checkout.

Fix `$REVIEW_FILE`. For each problem:

1. Open the file and find where the code you quoted actually is.
2. If the quote is real and you simply had the line wrong, correct the line number.
3. If the quote does not appear in that file at all, you have misremembered the code.
   Find what the file really says, and either rewrite the finding around the real code
   or delete the finding. Do not keep a finding whose evidence you cannot locate.
4. If the file has fewer lines than you cited, the citation was invented. Same rule.

Change nothing else — not the prose, not the severities, not the other findings. Use the
read tool to check each line before you write it; do not correct one guess with another.
When you are done, say only how many citations you corrected and how many findings you
removed.
