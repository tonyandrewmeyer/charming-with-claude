# Pebble: non-string environment values in layers

## Question

What happens if you pass a Pebble layer with non-string environment values
(e.g. `{'PORT': 8000}` instead of `{'PORT': '8000'}`) via the Python
`ops/pebble` client?

## Answer

It works. Pebble silently coerces the values to strings. The coercion is done
by Go's `gopkg.in/yaml.v3` library on the Pebble (server) side, not by the
Python `ops/pebble` client.

## How the data flows

### 1. Python `ops/pebble` — no validation

`Service.__init__` (`operator/ops/pebble.py`) stores environment as a plain
dict with no type checking:

```python
self.environment = dict(dct.get('environment', {}))
```

The `ServiceDict` TypedDict declares `'environment': dict[str, str]`, but
Python does not enforce TypedDict annotations at runtime. An integer value
passes through silently.

### 2. YAML serialization preserves native types

`Layer.to_yaml()` calls `yaml.safe_dump()`, which serializes Python ints and
bools as unquoted YAML scalars:

```yaml
# From {'PORT': 8000, 'DEBUG': True}
environment:
  PORT: 8000     # YAML integer
  DEBUG: true    # YAML boolean

# From {'PORT': '8000', 'DEBUG': 'true'}
environment:
  PORT: '8000'   # YAML string (quoted)
  DEBUG: 'true'  # YAML string (quoted)
```

### 3. Pebble receives the YAML and parses into `map[string]string`

The Go struct in `pebble/internals/plan/plan.go:229` is:

```go
Environment map[string]string `yaml:"environment,omitempty"`
```

When the YAML decoder encounters a scalar like `8000` (an integer) but the
target type is `string`, it uses the **raw text** of the YAML node rather than
the resolved typed value.

The relevant code is in `gopkg.in/yaml.v3@v3.0.1/decode.go:610-617`:

```go
switch out.Kind() {
case reflect.String:
    if tag == binaryTag {
        out.SetString(resolved.(string))
        return true
    }
    out.SetString(n.Value)  // uses raw YAML text, not resolved type
    return true
```

`n.Value` is always the original string representation from the YAML source
(e.g. `"8000"`, `"true"`, `"3.14"`), regardless of what YAML type the resolver
determined it to be. So unmarshalling into a `string` target never fails for
any scalar.

The yaml.v3 test suite confirms this explicitly (`decode_test.go:50-54`):

```go
// Same YAML, different Go target types:
{"v: true", map[string]string{"v": "true"}},       // -> string "true"
{"v: true", map[string]interface{}{"v": true}},     // -> bool true
```

## Verification

Running a live Pebble instance and sending a layer with mixed non-string
environment values:

```python
layer = Layer({
    'services': {
        'myapp': {
            'command': '/bin/echo hello',
            'override': 'replace',
            'environment': {'PORT': 8000, 'DEBUG': True, 'COUNT': 0, 'RATIO': 3.14},
        }
    }
})
client.add_layer('test', layer)
plan = client.get_plan()
for k, v in plan.services['myapp'].environment.items():
    print(f"  {k}: {v!r} (type={type(v).__name__})")
```

Output:

```
  COUNT: '0' (type=str)
  DEBUG: 'true' (type=str)
  PORT: '8000' (type=str)
  RATIO: '3.14' (type=str)
```

All values are accepted and returned as strings. No error.

## Summary

| Step | Component | What happens |
|------|-----------|-------------|
| Construction | `ops/pebble.py` `Service.__init__` | Stores `{'PORT': 8000}` as-is, no type check |
| Serialization | `ops/pebble.py` `Layer.to_yaml()` → `yaml.safe_dump` | Emits `PORT: 8000` (unquoted YAML int) |
| Transport | `ops/pebble.py` `Client.add_layer()` | Sends YAML string over HTTP to Pebble |
| Parsing | Pebble `plan.ParseLayer()` → `yaml.v3` decoder | Coerces `8000` to `"8000"` via `n.Value` into `map[string]string` |

The coercion is entirely on the Pebble/Go side. The Python client does nothing
to convert or validate environment value types.
