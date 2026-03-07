# Broader Sample Evaluation (L3-source, Sonnet 4.6)

All 5 charms migrated using Level 3 (source inspection) with Claude Sonnet 4.6.

## Results

| Charm | Team/Domain | Files Changed | Lines +/- | Time | Correctness | Completeness | Quality | Min Diff | Review | Total /25 |
|-------|-------------|:-------------:|:---------:|:----:|:-----------:|:------------:|:-------:|:--------:|:------:|:---------:|
| nginx-ingress-integrator | Networking | 5 | +220/-262 | 9m 53s | 5 | 5 | 4 | 4 | 4 | 22 |
| content-cache-k8s | Web Infra | 4 | +104/-147 | 7m 17s | 5 | 5 | 5 | 5 | 5 | 25 |
| indico | Web App/PaaS | 7 | +149/-231 | 9m 32s | 4 | 5 | 4 | 4 | 4 | 21 |
| loki-k8s | Observability | 18 | +396/-680 | 16m 45s | 4 | 5 | 4 | 4 | 4 | 21 |
| hockeypuck-k8s | Security | 4 | +176/-224 | 9m 01s | 4 | 5 | 4 | 4 | 4 | 21 |

## Observations

### content-cache-k8s (25/25 - perfect)
- Clean, minimal migration with correct API usage throughout
- Correctly used pytest-jubilant's pack() and juju fixture
- Proper handling of any-charm helper pattern
- No unnecessary changes

### nginx-ingress-integrator (22/25)
- Good migration of complex fixture setup (model constraints, ingress waiting)
- Correctly handled multi-relation tests and cert tests
- Minor: manually added --charm-file and --model-arch options instead of using pytest-jubilant built-ins
- Clean action execution migration (run_action -> juju.run)

### indico (21/25)
- Successfully migrated 7 files including complex SAML, S3, and Loki test modules
- Correctly handled container SSH via juju.ssh()
- Minor: some verbose status assertions after wait()
- Good handling of the complex multi-charm deployment (postgresql, redis, nginx)

### loki-k8s (21/25)
- Largest migration: 18 files, -1038 net lines (removed async boilerplate)
- Correctly migrated complex observability patterns (cross-model, cos-lite)
- Took longest (16m 45s) due to many files
- Minor: some helper functions could be simplified further
- Successfully handled ModelConfigChange context manager conversion

### hockeypuck-k8s (21/25)
- Successfully handled multi-model testing (juju_secondary via temp_model_factory)
- Correctly migrated cross-model key synchronisation tests
- Good handling of GPG key generation and HTTP API testing
- Properly converted pytest.mark.dependency chains
- Minor: temp_model_factory usage adds some verbosity

## s3-integrator Additional Runs

| Run | Lines +/- | Time | Correctness | Completeness | Quality | Min Diff | Review | Total /25 |
|-----|:---------:|:----:|:-----------:|:------------:|:-------:|:--------:|:------:|:---------:|
| L5-recipe-sonnet | +168/-218 | 8m 09s | 3 | 4 | 4 | 3 | 3 | 17 |
| L6-recipe-example-sonnet | +183/-207 | 7m 37s | 3 | 4 | 4 | 3 | 3 | 17 |

Both recipe-level runs hallucinated `successes=3` parameter in juju.wait(), created unnecessary .agent/state/ files, and used @pytest.mark.setup (non-standard). Consistent with saml-integrator findings.

## Key Takeaways

1. **L3-source works well across all complexity levels** — from simple (content-cache, 4 files) to complex (loki, 18 files)
2. **Time scales roughly with complexity** — 7min for simple, 10min for medium, 17min for large
3. **All migrations achieved completeness=5** — no files left unmigrated
4. **Multi-model testing handled correctly** — hockeypuck's temp_model_factory usage was correct
5. **No hallucinated APIs** in L3 runs — consistent advantage over recipe levels
6. **All would be mergeable with light review** — scores of 21-25 across the board
