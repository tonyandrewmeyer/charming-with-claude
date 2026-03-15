# fix: constrain juju controller volume with k8s snap

**Repository**: canonical/concierge
**Commit**: [826d1821](https://github.com/canonical/canonical/concierge/commit/826d1821a15df5489e2e2ff51bfbf395f0feaf1c)
**Date**: 2024-10-30T23:19:36+00:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | provisioning |
| Bug Type | edge-case |
| Severity | high |
| Fix Category | source-fix |

## Summary

Add root-disk constraint for juju bootstrap to prevent PVC allocation failure on small runners

## Commit Message

The K8s snap allocates local storage differently to MicroK8s,
it allocates persistent volumes using files which are presented
as blocks - the default size of the PVC is 20GiB in Juju, which
is too large on some Github Runners and prevents the controller
pod from starting.

## Changed Files

- M	internal/config/config_format.go
- M	internal/config/presets.go
- M	internal/juju/juju.go
- M	internal/juju/juju_test.go

## Diff

```diff
diff --git a/internal/config/config_format.go b/internal/config/config_format.go
index 1bc9b06..6ca6de4 100644
--- a/internal/config/config_format.go
+++ b/internal/config/config_format.go
@@ -18,6 +18,8 @@ type jujuConfig struct {
 	Channel string `mapstructure:"channel"`
 	// The set of model-defaults to be passed to Juju during bootstrap
 	ModelDefaults map[string]string `mapstructure:"model-defaults"`
+	// The set of bootstrap constraints to be passed to Juju
+	BootstrapConstraints map[string]string `mapstructure:"bootstrap-constraints"`
 }
 
 // providerConfig represents the set of providers to be configured and bootstrapped.
diff --git a/internal/config/presets.go b/internal/config/presets.go
index 095ef60..6c9f9fa 100644
--- a/internal/config/presets.go
+++ b/internal/config/presets.go
@@ -18,7 +18,7 @@ func Preset(preset string) (*Config, error) {
 	}
 }
 
-// defaultPackages is the default Juju config for all presets.
+// defaultJujuConfig is the default Juju config for all presets.
 var defaultJujuConfig jujuConfig = jujuConfig{
 	ModelDefaults: map[string]string{
 		"test-mode":                 "true",
@@ -86,7 +86,15 @@ var machinePreset *Config = &Config{
 // k8sPreset is a configuration preset designed to be used when testing
 // k8s charms.
 var k8sPreset *Config = &Config{
-	Juju: defaultJujuConfig,
+	Juju: jujuConfig{
+		ModelDefaults: map[string]string{
+			"test-mode":                 "true",
+			"automatically-retry-hooks": "false",
+		},
+		BootstrapConstraints: map[string]string{
+			"root-disk": "2G",
+		},
+	},
 	Providers: providerConfig{
 		// Enable LXD so charms can be built, but don't bootstrap onto it.
 		LXD: lxdConfig{Enable: true},
diff --git a/internal/juju/juju.go b/internal/juju/juju.go
index 694ba30..0efd59f 100644
--- a/internal/juju/juju.go
+++ b/internal/juju/juju.go
@@ -26,21 +26,23 @@ func NewJujuHandler(config *config.Config, runner runner.CommandRunner, provider
 	}
 
 	return &JujuHandler{
-		channel:       channel,
-		modelDefaults: config.Juju.ModelDefaults,
-		providers:     providers,
-		runner:        runner,
-		snaps:         []packages.SnapPackage{packages.NewSnap("juju", channel)},
+		channel:              channel,
+		bootstrapConstraints: config.Juju.BootstrapConstraints,
+		modelDefaults:        config.Juju.ModelDefaults,
+		providers:            providers,
+		runner:               runner,
+		snaps:                []packages.SnapPackage{packages.NewSnap("juju", channel)},
 	}
 }
 
 // JujuHandler represents a Juju installation on the system.
 type JujuHandler struct {
-	channel       string
-	modelDefaults map[string]string
-	providers     []providers.Provider
-	runner        runner.CommandRunner
-	snaps         []packages.SnapPackage
+	channel              string
+	bootstrapConstraints map[string]string
+	modelDefaults        map[string]string
+	providers            []providers.Provider
+	runner               runner.CommandRunner
+	snaps                []packages.SnapPackage
 }
 
 // Prepare bootstraps Juju on the configured providers.
@@ -197,18 +199,16 @@ func (j *JujuHandler) bootstrapProvider(provider providers.Provider) error {
 		"--verbose",
 	}
 
-	// Get a sorted list of the model-default keys
-	keys := make([]string, 0, len(j.modelDefaults))
-	for k := range j.modelDefaults {
-		keys = append(keys, k)
-	}
-	slices.Sort(keys)
-
 	// Iterate over the model-defaults and append them to the bootstrapArgs
-	for _, k := range keys {
+	for _, k := range sortedKeys(j.modelDefaults) {
 		bootstrapArgs = append(bootstrapArgs, "--model-default", fmt.Sprintf("%s=%s", k, j.modelDefaults[k]))
 	}
 
+	// Iterate over the bootstrap-constraints and append them to the bootstrapArgs
+	for _, k := range sortedKeys(j.bootstrapConstraints) {
+		bootstrapArgs = append(bootstrapArgs, "--bootstrap-constraints", fmt.Sprintf("%s=%s", k, j.bootstrapConstraints[k]))
+	}
+
 	user := j.runner.User().Username
 
 	cmd := runner.NewCommandAs(user, provider.GroupName(), "juju", bootstrapArgs)
@@ -269,3 +269,13 @@ func (j *JujuHandler) checkBootstrapped(controllerName string) (bool, error) {
 
 	return true, nil
 }
+
+// sortedKeys gets an alphabetically sorted list of keys from a map.
+func sortedKeys(m map[string]string) []string {
+	keys := make([]string, 0, len(m))
+	for k := range m {
+		keys = append(keys, k)
+	}
+	slices.Sort(keys)
+	return keys
+}
diff --git a/internal/juju/juju_test.go b/internal/juju/juju_test.go
index 0072c73..46633db 100644
--- a/internal/juju/juju_test.go
+++ b/internal/juju/juju_test.go
@@ -30,6 +30,7 @@ func setupHandlerWithPreset(preset string) (*runnertest.MockRunner, *JujuHandler
 	runner := runnertest.NewMockRunner()
 	runner.MockCommandReturn("sudo -u test-user juju show-controller concierge-lxd", []byte("not found"), fmt.Errorf("Test error"))
 	runner.MockCommandReturn("sudo -u test-user juju show-controller concierge-microk8s", []byte("not found"), fmt.Errorf("Test error"))
+	runner.MockCommandReturn("sudo -u test-user juju show-controller concierge-k8s", []byte("not found"), fmt.Errorf("Test error"))
 
 	cfg, err = config.Preset(preset)
 	if err != nil {
@@ -41,6 +42,8 @@ func setupHandlerWithPreset(preset string) (*runnertest.MockRunner, *JujuHandler
 		provider = providers.NewLXD(runner, cfg)
 	case "microk8s":
 		provider = providers.NewMicroK8s(runner, cfg)
+	case "k8s":
+		provider = providers.NewK8s(runner, cfg)
 	}
 
 	handler := NewJujuHandler(cfg, runner, []providers.Provider{provider})
@@ -101,6 +104,16 @@ func TestJujuHandlerCommandsPresets(t *testing.T) {
 			},
 			expectedDirs: []string{".local/share/juju"},
 		},
+		{
+			preset: "k8s",
+			expectedCommands: []string{
+				"snap install juju",
+				"sudo -u test-user juju show-controller concierge-k8s",
+				"sudo -u test-user juju bootstrap k8s concierge-k8s --verbose --model-default automatically-retry-hooks=false --model-default test-mode=true --bootstrap-constraints root-disk=2G",
+				"sudo -u test-user juju add-model -c concierge-k8s testing",
+			},
+			expectedDirs: []string{".local/share/juju"},
+		},
 	}
 
 	for _, tc := range tests {
```
