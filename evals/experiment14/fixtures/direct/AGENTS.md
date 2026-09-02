# Batch segmentation working agreement

Keep `contiguous_runs()` deterministic, preserve input order, never mutate the
caller-owned list, and finish with `python3 -m unittest -q`.
