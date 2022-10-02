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
# # init

# %% [markdown]
# This is an initialization cell that will be run for all tests below.

# %%
import csv
print("initialized")

# %% [markdown]
# # test: first thing
#

# %% [markdown]
# This is the first test. Will fail because hashlib hasn't been imported (the initializat comes after it.)

# %%
FILES_HASH_PERSON = b'MyApp Files Hash'
h = hashlib.blake2b(digest_size=32, person=FILES_HASH_PERSON)
h.update(b'the same content')
assert h.hexdigest() == '20d9cd024d4fb086aae819a1432dd2466de12947831b75c5a30cf2676095d3b4'


# %% [markdown]
# # init

# %% [markdown]
# This is a second initialization block. All the tests under it will also benefit from it being run before them, and it includes prior init blocks too.

# %%
import hashlib

# %% [markdown]
# # something else

# %% [markdown]
# This is not an init nor a test section. It is ignored.

# %%
raise TypeError

# %% [markdown]
# # test: second thing

# %% [markdown]
# This is the second test being run. The second initialization block is run before it and so hashlib is found.

# %%
FILES_HASH_PERSON = b'MyApp Files Hash'
h = hashlib.blake2b(digest_size=32, person=FILES_HASH_PERSON)
h.update(b'the same content')
assert h.hexdigest() == '20d9cd024d4fb086aae819a1432dd2466de12947831b75c5a30cf2676095d3b4'

