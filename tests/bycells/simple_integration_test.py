# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# The initialization cell above that will be run for all tests below.

# %%
import pytest
import hashlib
print("initialized")

# %% [markdown]
# # first test
#

# %% [markdown]
# This is the first test. Will fail because hashlib hasn't been imported (the initializat comes after it.)

# %%
FILES_HASH_PERSON = b'MyApp Files Hash'
h = hashlib.blake2b(digest_size=32, person=FILES_HASH_PERSON)
h.update(b'the same content')
assert h.hexdigest() == '20d9cd024d4fb086aae819a1432dd2466de12947831b75c5a30cf2676095d3b4'


# %% [markdown]
# # second test

# %% [markdown]
# This is the second test being run. The second initialization block is run before it and so hashlib is found.

# %%
FILES_HASH_PERSON = b'MyApp Files Hash'
h = hashlib.blake2b(digest_size=32, person=FILES_HASH_PERSON)
h.update(b'the same content')
assert h.hexdigest() == '20d9cd024d4fb086aae819a1432dd2466de12947831b75c5a30cf2676095d3b4'

