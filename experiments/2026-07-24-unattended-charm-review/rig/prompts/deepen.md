You wrote the review at `$REVIEW_FILE`, with working notes at `$NOTES_FILE`. You used
$USED_MIN minutes of a $BUDGET_MIN minute budget, so you stopped well before you had to.
That is not done — it is the parts that are easy to skip, left undone.

Go back and deepen it. Read your own review first, then pick up whatever it does not
already contain, in this order of value:

1. **Runtime behaviour you did not observe.** Failure injection especially: bad config
   values, removing a required relation while running, killing the workload process,
   restarting the unit, junk in a secret. Does it reach a sensible blocked status with a
   message an operator can act on, or does it traceback? Does it recover on its own?
2. **Integrations you did not exercise.** Relate it to another charm you have not tried
   yet — TLS, ingress, a database, observability — and watch what crosses the relation.
3. **Scale and lifecycle.** Scale up and back down, run every action, `juju refresh`
   between revisions if more than one exists, then remove the application and watch it
   tear down.
4. **The other environment.** The other Juju version, or the other substrate if the
   charm supports both. Differences between them are high-value findings.
5. **Code you skimmed.** The charm libraries it ships under `lib/charms/...`, the
   upgrade path, the parts of `src/` your findings do not mention.
6. **Its tests.** Run them. Report what fails and what is not covered relative to the
   risks you found.

Update `$REVIEW_FILE` in place — add findings, extend the observed-behaviour section,
sharpen the verdict. Keep everything already there that still holds; if something you
now know contradicts an earlier claim, correct it and say so. Append to `$NOTES_FILE`
as you go.

Anchor new claims to `file:line` and check the line by reading it before you write it —
line numbers from memory are wrong about half the time.
