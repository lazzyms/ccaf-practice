#!/usr/bin/env python3
"""Fourth-pass — fix Q314 weak distractors."""
import sys
sys.path.insert(0, '.')
from apply_improvements import apply, q

REPLACEMENTS = {

# Q314 line=404 — distractors 'Order of requests', 'Filename', 'Random UUID' too weak
404: q(
    "You're batching 100 documents. Failures must be retried only for the affected items. What identifies each batch item uniquely for targeted retry?",
    [
        "<code>custom_id</code> fields — you assign a unique ID to each request at submission; the batch API returns the same ID with each response, enabling precise failure identification",
        "Response order — batch results are not guaranteed to arrive in submission order; position-based correlation silently misassigns responses when the order shifts",
        "A content hash of the input document — hashes identify duplicate content but not unique request instances; identical documents would produce the same hash and be indistinguishable",
        "A timestamp assigned at submission time — timestamps have millisecond granularity that can collide within a large batch, making them unreliable as unique identifiers",
    ],
    "custom_id is the supported correlation mechanism: assign a unique identifier per request at submission, and the batch API returns it with the result. Response order is not guaranteed. Content hashes can't distinguish identical documents. Timestamps aren't unique enough for high-volume batches."
),

}

if __name__ == '__main__':
    apply(REPLACEMENTS)
