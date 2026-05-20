# fix(daemon): deduplicate user-provided notice types (#399)

**Repository**: pebble
**Commit**: [badafd96](https://github.com/canonical/pebble/commit/badafd96a8eee7874a897925f7dc547bb7831ed1)
**Date**: 2024-03-26T18:40:42-05:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | notices |
| Bug Type | data-validation |
| Severity | low |
| Fix Category | source-fix |

## Summary

Deduplicate user-provided notice types in API filter

## Commit Message

This is a subset of related changes made in snapd:
https://github.com/snapcore/snapd/pull/13673

Signed-off-by: Oliver Calder <oliver.calder@canonical.com>

## Changed Files

- M	internals/daemon/api_notices.go
- M	internals/daemon/api_notices_test.go

## Diff

```diff
diff --git a/internals/daemon/api_notices.go b/internals/daemon/api_notices.go
index 9e9c8f6..79630e4 100644
--- a/internals/daemon/api_notices.go
+++ b/internals/daemon/api_notices.go
@@ -1,4 +1,4 @@
-// Copyright (c) 2023 Canonical Ltd
+// Copyright (c) 2023-2024 Canonical Ltd
 //
 // This program is free software: you can redistribute it and/or modify
 // it under the terms of the GNU General Public License version 3 as
@@ -166,6 +166,7 @@ func sanitizeUserIDFilter(queryUserID []string) (*uint32, error) {
 // Construct the types filter which will be passed to state.Notices.
 func sanitizeTypesFilter(queryTypes []string) ([]state.NoticeType, error) {
 	typeStrs := strutil.MultiCommaSeparatedList(queryTypes)
+	alreadySeen := make(map[state.NoticeType]bool, len(typeStrs))
 	types := make([]state.NoticeType, 0, len(typeStrs))
 	for _, typeStr := range typeStrs {
 		noticeType := state.NoticeType(typeStr)
@@ -174,6 +175,10 @@ func sanitizeTypesFilter(queryTypes []string) ([]state.NoticeType, error) {
 			// with unknown types succeed).
 			continue
 		}
+		if alreadySeen[noticeType] {
+			continue
+		}
+		alreadySeen[noticeType] = true
 		types = append(types, noticeType)
 	}
 	if len(types) == 0 && len(typeStrs) > 0 {
diff --git a/internals/daemon/api_notices_test.go b/internals/daemon/api_notices_test.go
index 1050537..a6ac974 100644
--- a/internals/daemon/api_notices_test.go
+++ b/internals/daemon/api_notices_test.go
@@ -1,4 +1,4 @@
-// Copyright (c) 2023 Canonical Ltd
+// Copyright (c) 2023-2024 Canonical Ltd
 //
 // This program is free software: you can redistribute it and/or modify
 // it under the terms of the GNU General Public License version 3 as
@@ -157,7 +157,7 @@ func (s *apiSuite) TestNoticesFilterMultipleTypes(c *C) {
 	addNotice(c, st, nil, state.WarningNotice, "danger", nil)
 	st.Unlock()
 
-	req, err := http.NewRequest("GET", "/v1/notices?types=change-update&types=warning", nil)
+	req, err := http.NewRequest("GET", "/v1/notices?types=change-update&types=warning,warning", nil)
 	c.Assert(err, IsNil)
 	req.RemoteAddr = "pid=100;uid=1000;socket=;"
 	noticesCmd := apiCmd("/v1/notices")
```
