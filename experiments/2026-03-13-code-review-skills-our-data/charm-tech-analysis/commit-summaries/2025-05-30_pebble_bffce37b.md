# fix: avoid panic when Pebble restarts after stop-checks (#625)

**Repository**: pebble
**Commit**: [bffce37b](https://github.com/canonical/pebble/commit/bffce37b7a6317120affe8adfa72eca143973ea4)
**Date**: 2025-05-30T13:13:33+12:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | checks |
| Bug Type | nil-pointer |
| Severity | high |
| Fix Category | source-fix |

## Summary

Fix panic on Pebble restart after stop-checks by removing invalid SetStatus call on aborted change (backport)

## Commit Message

Calling change.Abort() is enough. We had previously added the SetStatus
in commit f9250f69a92f297fb7f1bfbe16b145605ca71262 as the test was
seeing a Hold status, but that was because it hadn't done an Ensure to
actually move the checks to Doing. So fix the test as well, and the
change should end up as Done.

Fixes #621

## Changed Files

- M	internals/overlord/checkstate/manager.go
- M	internals/overlord/checkstate/manager_test.go

## Diff

```diff
diff --git a/internals/overlord/checkstate/manager.go b/internals/overlord/checkstate/manager.go
index 1534955..4f6daf1 100644
--- a/internals/overlord/checkstate/manager.go
+++ b/internals/overlord/checkstate/manager.go
@@ -600,7 +600,6 @@ func (m *CheckManager) StopChecks(checks []string) (stopped []string, err error)
 		change := m.state.Change(checkData.changeID)
 		if change != nil {
 			change.Abort()
-			change.SetStatus(state.AbortStatus)
 			stopped = append(stopped, check.Name)
 		}
 		// We pass in the current number of failures so that it remains the
diff --git a/internals/overlord/checkstate/manager_test.go b/internals/overlord/checkstate/manager_test.go
index 210725c..2c4fe79 100644
--- a/internals/overlord/checkstate/manager_test.go
+++ b/internals/overlord/checkstate/manager_test.go
@@ -737,39 +737,80 @@ func (s *ManagerSuite) TestStopChecks(c *C) {
 	}
 	err := s.planMgr.AppendLayer(origLayer, false)
 	c.Assert(err, IsNil)
+
+	// Run an Ensure pass to kick the check tasks into Doing status.
+	st := s.overlord.State()
+	st.EnsureBefore(0)
+
 	waitChecks(c, s.manager, []*checkstate.CheckInfo{
 		{Name: "chk1", Startup: "enabled", Status: "up", Threshold: 3},
 		{Name: "chk2", Startup: "disabled", Status: "inactive", Threshold: 3},
 		{Name: "chk3", Startup: "enabled", Status: "up", Threshold: 3},
 	})
+
 	checks, err := s.manager.Checks()
 	c.Assert(err, IsNil)
-	var originalChangeIDs []string
+	var chk1ChangeID, chk3ChangeID string
 	for _, check := range checks {
-		originalChangeIDs = append(originalChangeIDs, check.ChangeID)
+		switch check.Name {
+		case "chk1":
+			chk1ChangeID = check.ChangeID
+		case "chk3":
+			chk3ChangeID = check.ChangeID
+		}
+	}
+	c.Assert(chk1ChangeID, Not(Equals), "")
+	c.Assert(chk3ChangeID, Not(Equals), "")
+
+	start := time.Now()
+	for {
+		if time.Since(start) > 3*time.Second {
+			c.Fatal("timed out waiting for check changes to go to Doing")
+		}
+		st.Lock()
+		chk1Status := st.Change(chk1ChangeID).Status()
+		chk3Status := st.Change(chk3ChangeID).Status()
+		st.Unlock()
+		if chk1Status == state.DoingStatus && chk3Status == state.DoingStatus {
+			break
+		}
+		time.Sleep(10 * time.Millisecond)
 	}
 
 	changed, err := s.manager.StopChecks([]string{"chk1", "chk2"})
+	c.Assert(err, IsNil)
+	c.Assert(changed, DeepEquals, []string{"chk1"})
+
+	// Run an Ensure pass to actually stop the checks.
+	st.EnsureBefore(0)
+
 	waitChecks(c, s.manager, []*checkstate.CheckInfo{
 		{Name: "chk1", Startup: "enabled", Status: "inactive", Threshold: 3},
 		{Name: "chk2", Startup: "disabled", Status: "inactive", Threshold: 3},
 		{Name: "chk3", Startup: "enabled", Status: "up", Threshold: 3},
 	})
-	c.Assert(err, IsNil)
-	c.Assert(changed, DeepEquals, []string{"chk1"})
+
+	// chk3 should still have the same change ID, chk1 and chk2 should not have one.
 	checks, err = s.manager.Checks()
 	c.Assert(err, IsNil)
-	// chk3 should still have the same change ID, chk1 and chk2 should not have one.
 	c.Assert(checks[0].ChangeID, Equals, "")
 	c.Assert(checks[1].ChangeID, Equals, "")
-	c.Assert(checks[2].ChangeID, Equals, originalChangeIDs[2])
-	// chk1's old Change should have aborted.
-	st := s.overlord.State()
-	st.Lock()
-	change := st.Change(originalChangeIDs[0])
-	status := change.Status()
-	st.Unlock()
-	c.Assert(status, Equals, state.AbortStatus)
+	c.Assert(checks[2].ChangeID, Equals, chk3ChangeID)
+
+	// chk1's old change should go to Done.
+	start = time.Now()
+	for {
+		if time.Since(start) > 3*time.Second {
+			c.Fatal("timed out waiting for check changes to go to Done")
+		}
+		st.Lock()
+		chk1Status := st.Change(chk1ChangeID).Status()
+		st.Unlock()
+		if chk1Status == state.DoneStatus {
+			break
+		}
+		time.Sleep(10 * time.Millisecond)
+	}
 }
 
 func (s *ManagerSuite) TestStopChecksNotFound(c *C) {
```
